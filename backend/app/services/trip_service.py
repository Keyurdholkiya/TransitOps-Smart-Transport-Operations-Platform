from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.driver import Driver
from app.models.fleet_enums import DriverStatus, VehicleStatus
from app.models.trip import Trip
from app.models.trip_enums import TripStatus, TripType
from app.models.vehicle import Vehicle
from app.repositories.driver_repository import DriverRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.trip import (
    TripCancellationRequest,
    TripCompletionRequest,
    TripCreate,
)
from app.services.fleet_rules import (
    ensure_driver_dispatchable,
    ensure_vehicle_dispatchable,
    validate_cargo_capacity,
)


class TripService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = TripRepository(session)
        self.vehicle_repository = VehicleRepository(session)
        self.driver_repository = DriverRepository(session)

    def create_trip(self, trip_data: TripCreate) -> Trip:
        existing_trip = self.repository.get_by_trip_number(
            trip_data.trip_number,
        )

        if existing_trip is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A trip with this trip number already exists.",
            )

        vehicle = self.vehicle_repository.get_by_id(
            trip_data.vehicle_id,
        )

        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found.",
            )

        driver = self.driver_repository.get_by_id(
            trip_data.driver_id,
        )

        if driver is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found.",
            )

        validate_cargo_capacity(
            vehicle,
            trip_data.cargo_weight_kg,
        )

        try:
            trip = self.repository.create(trip_data)
            self.session.commit()
            self.session.refresh(trip)
            return trip
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trip could not be created because of conflicting data.",
            ) from exc

    def get_trip(self, trip_id: UUID) -> Trip:
        trip = self.repository.get_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found.",
            )

        return trip

    def list_trips(
        self,
        *,
        offset: int,
        limit: int,
        trip_status: TripStatus | None,
        trip_type: TripType | None,
        vehicle_id: UUID | None,
        driver_id: UUID | None,
    ) -> tuple[list[Trip], int]:
        trips = list(
            self.repository.list_trips(
                offset=offset,
                limit=limit,
                status=trip_status,
                trip_type=trip_type,
                vehicle_id=vehicle_id,
                driver_id=driver_id,
            ),
        )
        total = self.repository.count_trips(
            status=trip_status,
            trip_type=trip_type,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
        )

        return trips, total

    def dispatch_trip(self, trip_id: UUID) -> Trip:
        try:
            trip = self._get_locked_trip(trip_id)

            if trip.status != TripStatus.PLANNED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Only a planned trip can be dispatched.",
                )

            vehicle, driver = self._get_locked_resources(trip)

            ensure_vehicle_dispatchable(vehicle)
            ensure_driver_dispatchable(driver)
            validate_cargo_capacity(
                vehicle,
                trip.cargo_weight_kg,
            )

            active_vehicle_trip = self.repository.get_active_by_vehicle_id(
                vehicle.id,
                exclude_trip_id=trip.id,
            )

            if active_vehicle_trip is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Vehicle is already assigned to an active trip.",
                )

            active_driver_trip = self.repository.get_active_by_driver_id(
                driver.id,
                exclude_trip_id=trip.id,
            )

            if active_driver_trip is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Driver is already assigned to an active trip.",
                )

            operation_time = utc_now()

            trip.status = TripStatus.IN_PROGRESS
            trip.dispatched_at = operation_time
            vehicle.status = VehicleStatus.ON_TRIP
            driver.status = DriverStatus.ON_TRIP

            self.repository.save(trip)
            self.vehicle_repository.save(vehicle)
            self.driver_repository.save(driver)

            self.session.commit()
            self.session.refresh(trip)

            return trip
        except HTTPException:
            self.session.rollback()
            raise
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "The vehicle or driver was assigned by another dispatch operation."
                ),
            ) from exc
        except Exception:
            self.session.rollback()
            raise

    def complete_trip(
        self,
        trip_id: UUID,
        completion_data: TripCompletionRequest,
    ) -> Trip:
        try:
            trip = self._get_locked_trip(trip_id)

            if trip.status != TripStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Only an in-progress trip can be completed.",
                )

            vehicle, driver = self._get_locked_resources(trip)
            final_odometer = completion_data.final_odometer_km

            if final_odometer is not None and final_odometer < vehicle.odometer_km:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Final odometer cannot be lower than the "
                        "vehicle's current odometer."
                    ),
                )

            operation_time = utc_now()

            if final_odometer is not None:
                vehicle.odometer_km = final_odometer
                trip.final_odometer_km = final_odometer

            trip.status = TripStatus.COMPLETED
            trip.completed_at = operation_time
            vehicle.status = VehicleStatus.AVAILABLE
            driver.status = DriverStatus.AVAILABLE

            self.repository.save(trip)
            self.vehicle_repository.save(vehicle)
            self.driver_repository.save(driver)

            self.session.commit()
            self.session.refresh(trip)

            return trip
        except HTTPException:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise

    def cancel_trip(
        self,
        trip_id: UUID,
        cancellation_data: TripCancellationRequest,
    ) -> Trip:
        try:
            trip = self._get_locked_trip(trip_id)

            if trip.status == TripStatus.COMPLETED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A completed trip cannot be cancelled.",
                )

            if trip.status == TripStatus.CANCELLED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Trip is already cancelled.",
                )

            operation_time = utc_now()

            if trip.status == TripStatus.IN_PROGRESS:
                vehicle, driver = self._get_locked_resources(trip)

                vehicle.status = VehicleStatus.AVAILABLE
                driver.status = DriverStatus.AVAILABLE

                self.vehicle_repository.save(vehicle)
                self.driver_repository.save(driver)

            trip.status = TripStatus.CANCELLED
            trip.cancelled_at = operation_time
            trip.cancellation_reason = cancellation_data.reason

            self.repository.save(trip)
            self.session.commit()
            self.session.refresh(trip)

            return trip
        except HTTPException:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise

    def _get_locked_trip(self, trip_id: UUID) -> Trip:
        trip = self.repository.get_by_id_for_update(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found.",
            )

        return trip

    def _get_locked_resources(
        self,
        trip: Trip,
    ) -> tuple[Vehicle, Driver]:
        vehicle = self.vehicle_repository.get_by_id_for_update(
            trip.vehicle_id,
        )

        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle assigned to the trip was not found.",
            )

        driver = self.driver_repository.get_by_id_for_update(
            trip.driver_id,
        )

        if driver is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver assigned to the trip was not found.",
            )

        return vehicle, driver

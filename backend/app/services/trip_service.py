from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.models.trip_enums import TripStatus, TripType
from app.repositories.driver_repository import DriverRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.trip import TripCreate
from app.services.fleet_rules import validate_cargo_capacity


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

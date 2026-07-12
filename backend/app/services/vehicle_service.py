from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.fleet_enums import VehicleStatus, VehicleType
from app.models.vehicle import Vehicle
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = VehicleRepository(session)

    def create_vehicle(self, vehicle_data: VehicleCreate) -> Vehicle:
        existing_vehicle = self.repository.get_by_registration_number(
            vehicle_data.registration_number,
        )

        if existing_vehicle is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A vehicle with this registration number already exists.",
            )

        try:
            vehicle = self.repository.create(vehicle_data)
            self.session.commit()
            self.session.refresh(vehicle)
            return vehicle
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vehicle registration number already exists.",
            ) from exc

    def get_vehicle(self, vehicle_id: UUID) -> Vehicle:
        vehicle = self.repository.get_by_id(vehicle_id)

        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found.",
            )

        return vehicle

    def list_vehicles(
        self,
        *,
        offset: int,
        limit: int,
        vehicle_status: VehicleStatus | None,
        vehicle_type: VehicleType | None,
    ) -> tuple[list[Vehicle], int]:
        vehicles = list(
            self.repository.list_vehicles(
                offset=offset,
                limit=limit,
                status=vehicle_status,
                vehicle_type=vehicle_type,
            ),
        )
        total = self.repository.count_vehicles(
            status=vehicle_status,
            vehicle_type=vehicle_type,
        )

        return vehicles, total

    def update_vehicle(
        self,
        vehicle_id: UUID,
        vehicle_data: VehicleUpdate,
    ) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)

        if vehicle.status == VehicleStatus.RETIRED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A retired vehicle cannot be modified.",
            )

        if vehicle.status == VehicleStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A vehicle currently on a trip cannot be modified.",
            )

        changes = vehicle_data.model_dump(exclude_unset=True)

        if not changes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one vehicle field must be provided.",
            )

        if any(value is None for value in changes.values()):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Vehicle fields cannot be null.",
            )

        new_registration = changes.get("registration_number")

        if new_registration is not None:
            existing_vehicle = self.repository.get_by_registration_number(
                new_registration,
            )
            if existing_vehicle is not None and existing_vehicle.id != vehicle.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Vehicle registration number already exists.",
                )

        for field_name, value in changes.items():
            setattr(vehicle, field_name, value)

        try:
            vehicle = self.repository.save(vehicle)
            self.session.commit()
            self.session.refresh(vehicle)
            return vehicle
        except IntegrityError as exc:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vehicle registration number already exists.",
            ) from exc

    def update_status(
        self,
        vehicle_id: UUID,
        new_status: VehicleStatus,
    ) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)

        if vehicle.status == new_status:
            return vehicle

        if vehicle.status == VehicleStatus.RETIRED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A retired vehicle cannot return to service.",
            )

        if vehicle.status == VehicleStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trip status must be changed through trip operations.",
            )

        if new_status == VehicleStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A vehicle can enter on-trip status only through dispatch.",
            )

        vehicle.status = new_status
        vehicle = self.repository.save(vehicle)
        self.session.commit()
        self.session.refresh(vehicle)

        return vehicle

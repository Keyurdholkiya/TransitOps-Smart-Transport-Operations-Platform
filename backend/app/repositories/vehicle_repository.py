from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.fleet_enums import VehicleStatus, VehicleType
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate


class VehicleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        return self.session.get(Vehicle, vehicle_id)

    def get_by_id_for_update(self, vehicle_id: UUID) -> Vehicle | None:
        statement = select(Vehicle).where(Vehicle.id == vehicle_id).with_for_update()
        return self.session.scalar(statement)

    def get_by_registration_number(
        self,
        registration_number: str,
    ) -> Vehicle | None:
        statement = select(Vehicle).where(
            Vehicle.registration_number == registration_number.strip().upper(),
        )
        return self.session.scalar(statement)

    def list_vehicles(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        status: VehicleStatus | None = None,
        vehicle_type: VehicleType | None = None,
    ) -> Sequence[Vehicle]:
        statement = select(Vehicle)

        if status is not None:
            statement = statement.where(Vehicle.status == status)

        if vehicle_type is not None:
            statement = statement.where(Vehicle.vehicle_type == vehicle_type)

        statement = (
            statement.order_by(
                Vehicle.created_at.desc(),
                Vehicle.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        return self.session.scalars(statement).all()

    def count_vehicles(
        self,
        *,
        status: VehicleStatus | None = None,
        vehicle_type: VehicleType | None = None,
    ) -> int:
        statement = select(func.count()).select_from(Vehicle)

        if status is not None:
            statement = statement.where(Vehicle.status == status)

        if vehicle_type is not None:
            statement = statement.where(Vehicle.vehicle_type == vehicle_type)

        return self.session.scalar(statement) or 0

    def create(self, vehicle_data: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(
            registration_number=vehicle_data.registration_number,
            vehicle_type=vehicle_data.vehicle_type,
            manufacturer=vehicle_data.manufacturer,
            model=vehicle_data.model,
            manufacturing_year=vehicle_data.manufacturing_year,
            capacity_kg=vehicle_data.capacity_kg,
            odometer_km=vehicle_data.odometer_km,
            status=VehicleStatus.AVAILABLE,
        )

        self.session.add(vehicle)
        self.session.flush()
        self.session.refresh(vehicle)

        return vehicle

    def save(self, vehicle: Vehicle) -> Vehicle:
        self.session.add(vehicle)
        self.session.flush()
        self.session.refresh(vehicle)

        return vehicle

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.models.trip_enums import TripStatus, TripType
from app.schemas.trip import TripCreate


class TripRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, trip_id: UUID) -> Trip | None:
        return self.session.get(Trip, trip_id)

    def get_by_id_for_update(self, trip_id: UUID) -> Trip | None:
        statement = select(Trip).where(Trip.id == trip_id).with_for_update()
        return self.session.scalar(statement)

    def get_by_trip_number(self, trip_number: str) -> Trip | None:
        normalized_trip_number = "".join(trip_number.strip().upper().split())
        statement = select(Trip).where(
            Trip.trip_number == normalized_trip_number,
        )
        return self.session.scalar(statement)

    def get_active_by_vehicle_id(
        self,
        vehicle_id: UUID,
        *,
        exclude_trip_id: UUID | None = None,
    ) -> Trip | None:
        statement = select(Trip).where(
            Trip.vehicle_id == vehicle_id,
            Trip.status == TripStatus.IN_PROGRESS,
        )

        if exclude_trip_id is not None:
            statement = statement.where(Trip.id != exclude_trip_id)

        return self.session.scalar(statement)

    def get_active_by_driver_id(
        self,
        driver_id: UUID,
        *,
        exclude_trip_id: UUID | None = None,
    ) -> Trip | None:
        statement = select(Trip).where(
            Trip.driver_id == driver_id,
            Trip.status == TripStatus.IN_PROGRESS,
        )

        if exclude_trip_id is not None:
            statement = statement.where(Trip.id != exclude_trip_id)

        return self.session.scalar(statement)

    def list_trips(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        status: TripStatus | None = None,
        trip_type: TripType | None = None,
        vehicle_id: UUID | None = None,
        driver_id: UUID | None = None,
    ) -> Sequence[Trip]:
        statement = select(Trip)

        if status is not None:
            statement = statement.where(Trip.status == status)

        if trip_type is not None:
            statement = statement.where(Trip.trip_type == trip_type)

        if vehicle_id is not None:
            statement = statement.where(Trip.vehicle_id == vehicle_id)

        if driver_id is not None:
            statement = statement.where(Trip.driver_id == driver_id)

        statement = (
            statement.order_by(
                Trip.created_at.desc(),
                Trip.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        return self.session.scalars(statement).all()

    def count_trips(
        self,
        *,
        status: TripStatus | None = None,
        trip_type: TripType | None = None,
        vehicle_id: UUID | None = None,
        driver_id: UUID | None = None,
    ) -> int:
        statement = select(func.count()).select_from(Trip)

        if status is not None:
            statement = statement.where(Trip.status == status)

        if trip_type is not None:
            statement = statement.where(Trip.trip_type == trip_type)

        if vehicle_id is not None:
            statement = statement.where(Trip.vehicle_id == vehicle_id)

        if driver_id is not None:
            statement = statement.where(Trip.driver_id == driver_id)

        return self.session.scalar(statement) or 0

    def create(self, trip_data: TripCreate) -> Trip:
        trip = Trip(
            trip_number=trip_data.trip_number,
            vehicle_id=trip_data.vehicle_id,
            driver_id=trip_data.driver_id,
            trip_type=trip_data.trip_type,
            origin=trip_data.origin,
            destination=trip_data.destination,
            cargo_weight_kg=trip_data.cargo_weight_kg,
            scheduled_departure_at=trip_data.scheduled_departure_at,
            status=TripStatus.PLANNED,
        )

        self.session.add(trip)
        self.session.flush()
        self.session.refresh(trip)

        return trip

    def save(self, trip: Trip) -> Trip:
        self.session.add(trip)
        self.session.flush()
        self.session.refresh(trip)

        return trip

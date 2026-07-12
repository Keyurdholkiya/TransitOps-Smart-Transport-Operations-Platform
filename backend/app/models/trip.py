from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin
from app.models.trip_enums import TripStatus, TripType


class Trip(TimestampMixin, Base):
    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint(
            "cargo_weight_kg > 0",
            name="ck_trips_cargo_weight_positive",
        ),
        CheckConstraint(
            "final_odometer_km IS NULL OR final_odometer_km >= 0",
            name="ck_trips_final_odometer_non_negative",
        ),
        Index(
            "uq_trips_active_vehicle",
            "vehicle_id",
            unique=True,
            postgresql_where=text("status = 'in_progress'"),
        ),
        Index(
            "uq_trips_active_driver",
            "driver_id",
            unique=True,
            postgresql_where=text("status = 'in_progress'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    trip_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    vehicle_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "vehicles.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=False,
    )
    driver_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "drivers.id",
            ondelete="RESTRICT",
        ),
        index=True,
        nullable=False,
    )
    trip_type: Mapped[TripType] = mapped_column(
        Enum(
            TripType,
            name="trip_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
    )
    origin: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    cargo_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    status: Mapped[TripStatus] = mapped_column(
        Enum(
            TripStatus,
            name="trip_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        default=TripStatus.PLANNED,
        server_default=TripStatus.PLANNED.value,
        index=True,
        nullable=False,
    )
    scheduled_departure_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    dispatched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    final_odometer_km: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

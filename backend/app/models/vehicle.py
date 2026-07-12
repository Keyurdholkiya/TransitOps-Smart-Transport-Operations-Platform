from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Enum,
    Numeric,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.fleet_enums import VehicleStatus, VehicleType
from app.models.mixins import TimestampMixin


class Vehicle(TimestampMixin, Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint(
            "manufacturing_year >= 1980",
            name="ck_vehicles_manufacturing_year",
        ),
        CheckConstraint(
            "capacity_kg > 0",
            name="ck_vehicles_capacity_positive",
        ),
        CheckConstraint(
            "odometer_km >= 0",
            name="ck_vehicles_odometer_non_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    registration_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )
    vehicle_type: Mapped[VehicleType] = mapped_column(
        Enum(
            VehicleType,
            name="vehicle_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
    )
    manufacturer: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    manufacturing_year: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )
    capacity_kg: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    odometer_km: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        server_default=text("0.00"),
        nullable=False,
    )
    status: Mapped[VehicleStatus] = mapped_column(
        Enum(
            VehicleStatus,
            name="vehicle_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        default=VehicleStatus.AVAILABLE,
        server_default=VehicleStatus.AVAILABLE.value,
        index=True,
        nullable=False,
    )

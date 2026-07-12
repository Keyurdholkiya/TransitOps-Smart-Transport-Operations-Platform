from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, Enum, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.fleet_enums import DriverStatus
from app.models.mixins import TimestampMixin


class Driver(TimestampMixin, Base):
    __tablename__ = "drivers"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    employee_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String(320),
        unique=True,
        nullable=True,
    )
    phone_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    licence_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    licence_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    licence_expiry_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False,
    )
    joining_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    status: Mapped[DriverStatus] = mapped_column(
        Enum(
            DriverStatus,
            name="driver_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        default=DriverStatus.AVAILABLE,
        server_default=DriverStatus.AVAILABLE.value,
        index=True,
        nullable=False,
    )

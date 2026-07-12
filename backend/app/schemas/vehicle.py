from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.fleet_enums import VehicleStatus, VehicleType


def normalize_registration_number(value: str) -> str:
    normalized = "".join(value.strip().upper().split())

    if not normalized:
        raise ValueError("Registration number cannot be empty.")

    return normalized


def normalize_required_text(value: str) -> str:
    normalized = " ".join(value.strip().split())

    if not normalized:
        raise ValueError("Value cannot be empty.")

    return normalized


class VehicleBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    registration_number: str = Field(
        min_length=2,
        max_length=30,
    )
    vehicle_type: VehicleType
    manufacturer: str = Field(
        min_length=1,
        max_length=100,
    )
    model: str = Field(
        min_length=1,
        max_length=100,
    )
    manufacturing_year: int = Field(
        ge=1980,
        le=2100,
    )
    capacity_kg: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    odometer_km: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    @field_validator("registration_number", mode="before")
    @classmethod
    def validate_registration_number(cls, value: str) -> str:
        return normalize_registration_number(value)

    @field_validator("manufacturer", "model", mode="before")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return normalize_required_text(value)


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    registration_number: str | None = Field(
        default=None,
        min_length=2,
        max_length=30,
    )
    vehicle_type: VehicleType | None = None
    manufacturer: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    manufacturing_year: int | None = Field(
        default=None,
        ge=1980,
        le=2100,
    )
    capacity_kg: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    odometer_km: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    @field_validator("registration_number", mode="before")
    @classmethod
    def validate_registration_number(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_registration_number(value)

    @field_validator("manufacturer", "model", mode="before")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_required_text(value)


class VehicleStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: VehicleStatus


class VehicleResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    id: UUID
    registration_number: str
    vehicle_type: VehicleType
    manufacturer: str
    model: str
    manufacturing_year: int
    capacity_kg: Decimal
    odometer_km: Decimal
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime

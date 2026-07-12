from datetime import UTC, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.trip_enums import TripStatus, TripType
from app.schemas.vehicle import normalize_required_text


def normalize_trip_number(value: str) -> str:
    normalized = "".join(value.strip().upper().split())

    if not normalized:
        raise ValueError("Trip number cannot be empty.")

    return normalized


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = " ".join(value.strip().split())
    return normalized or None


def normalize_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Datetime must include timezone information.")

    return value.astimezone(UTC)


class TripBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trip_number: str = Field(
        min_length=1,
        max_length=50,
    )
    vehicle_id: UUID
    driver_id: UUID
    trip_type: TripType
    origin: str = Field(
        min_length=2,
        max_length=255,
    )
    destination: str = Field(
        min_length=2,
        max_length=255,
    )
    cargo_weight_kg: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    scheduled_departure_at: datetime | None = None

    @field_validator("trip_number", mode="before")
    @classmethod
    def validate_trip_number(cls, value: str) -> str:
        return normalize_trip_number(value)

    @field_validator("origin", "destination", mode="before")
    @classmethod
    def validate_location(cls, value: str) -> str:
        return normalize_required_text(value)

    @field_validator("scheduled_departure_at")
    @classmethod
    def validate_scheduled_departure(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        return normalize_utc_datetime(value)

    @model_validator(mode="after")
    def validate_route(self) -> Self:
        if self.origin.casefold() == self.destination.casefold():
            raise ValueError("Origin and destination must be different.")

        return self


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_id: UUID | None = None
    driver_id: UUID | None = None
    trip_type: TripType | None = None
    origin: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )
    destination: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )
    cargo_weight_kg: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    scheduled_departure_at: datetime | None = None

    @field_validator("origin", "destination", mode="before")
    @classmethod
    def validate_location(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_required_text(value)

    @field_validator("scheduled_departure_at")
    @classmethod
    def validate_scheduled_departure(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        return normalize_utc_datetime(value)


class TripCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    final_odometer_km: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )


class TripCancellationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(
        min_length=3,
        max_length=500,
    )

    @field_validator("reason", mode="before")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return normalize_required_text(value)


class TripResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    id: UUID
    trip_number: str
    vehicle_id: UUID
    driver_id: UUID
    trip_type: TripType
    origin: str
    destination: str
    cargo_weight_kg: Decimal
    status: TripStatus
    scheduled_departure_at: datetime | None
    dispatched_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    final_odometer_km: Decimal | None
    created_at: datetime
    updated_at: datetime


class TripListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[TripResponse]
    total: int
    offset: int
    limit: int

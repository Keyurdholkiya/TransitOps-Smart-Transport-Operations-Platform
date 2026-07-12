from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.fleet_enums import DriverStatus
from app.schemas.vehicle import normalize_required_text


def normalize_identifier(value: str) -> str:
    normalized = "".join(value.strip().upper().split())

    if not normalized:
        raise ValueError("Identifier cannot be empty.")

    return normalized


def normalize_phone_number(value: str) -> str:
    normalized = value.strip().replace(" ", "")

    if not normalized:
        raise ValueError("Phone number cannot be empty.")

    allowed_characters = set("+0123456789-")

    if any(character not in allowed_characters for character in normalized):
        raise ValueError("Phone number contains invalid characters.")

    return normalized


class DriverBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_code: str = Field(
        min_length=1,
        max_length=50,
    )
    full_name: str = Field(
        min_length=2,
        max_length=150,
    )
    email: EmailStr | None = None
    phone_number: str = Field(
        min_length=7,
        max_length=30,
    )
    licence_number: str = Field(
        min_length=3,
        max_length=50,
    )
    licence_category: str = Field(
        min_length=1,
        max_length=50,
    )
    licence_expiry_date: date
    joining_date: date

    @field_validator("employee_code", "licence_number", mode="before")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        return normalize_identifier(value)

    @field_validator("full_name", "licence_category", mode="before")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return normalize_required_text(value)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()
        return normalized or None

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return normalize_phone_number(value)


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    email: EmailStr | None = None
    phone_number: str | None = Field(
        default=None,
        min_length=7,
        max_length=30,
    )
    licence_number: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )
    licence_category: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    licence_expiry_date: date | None = None
    joining_date: date | None = None

    @field_validator("employee_code", "licence_number", mode="before")
    @classmethod
    def validate_identifier(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_identifier(value)

    @field_validator("full_name", "licence_category", mode="before")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_required_text(value)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()
        return normalized or None

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return normalize_phone_number(value)


class DriverStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: DriverStatus


class DriverResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    id: UUID
    employee_code: str
    full_name: str
    email: EmailStr | None
    phone_number: str
    licence_number: str
    licence_category: str
    licence_expiry_date: date
    joining_date: date
    status: DriverStatus
    created_at: datetime
    updated_at: datetime

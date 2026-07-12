from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)

from app.models.role import RoleName


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, value: object) -> object:
        if isinstance(value, str):
            return " ".join(value.split())
        return value


class UserCreate(UserBase):
    password: SecretStr
    role: RoleName

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()

        if len(password) < 12:
            raise ValueError("Password must contain at least 12 characters.")

        if len(password) > 128:
            raise ValueError("Password must contain at most 128 characters.")

        return value


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    role: RoleName | None = None
    is_active: bool | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, value: object) -> object:
        if isinstance(value, str):
            return " ".join(value.split())
        return value


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: RoleName
    display_name: str
    description: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    role: RoleResponse
    created_at: datetime
    updated_at: datetime

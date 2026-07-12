from functools import lru_cache
from typing import Literal

from pydantic import EmailStr, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "TransitOps API"
    app_description: str = (
        "Backend API for the TransitOps Smart Transport Operations Platform."
    )
    app_version: str = "0.1.0"
    app_env: Literal["local", "development", "testing", "production"] = "local"
    app_debug: bool = True

    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+psycopg://transitops:transitops@127.0.0.1:5433/transitops"
    )

    secret_key: str = Field(min_length=32)

    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_issuer: str = "transitops-api"
    jwt_audience: str = "transitops-web"
    access_token_expire_minutes: int = Field(
        default=30,
        ge=5,
        le=1440,
    )

    initial_admin_email: EmailStr | None = None
    initial_admin_password: SecretStr | None = None
    initial_admin_full_name: str = "TransitOps Administrator"

    allowed_origins: list[str] = [
        "http://localhost:5173",
    ]

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    allowed_hosts: list[str] = [
        "localhost",
        "127.0.0.1",
        "testserver",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

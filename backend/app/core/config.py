from functools import lru_cache
from typing import Literal

from pydantic import Field
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

    allowed_origins: list[str] = [
        "http://localhost:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
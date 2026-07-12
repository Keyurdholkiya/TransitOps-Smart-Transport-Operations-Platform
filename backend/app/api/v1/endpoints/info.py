from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/info", tags=["Application"])

@router.get("")
def application_info() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }
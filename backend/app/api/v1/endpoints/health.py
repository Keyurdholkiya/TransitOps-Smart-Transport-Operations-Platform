from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "TransitOps API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
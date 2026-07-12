from datetime import UTC, datetime

from fastapi import APIRouter, Response, status
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import check_database_connection

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check(response: Response) -> dict[str, str]:
    application_status = "healthy"
    database_status = "connected"

    try:
        check_database_connection()
    except SQLAlchemyError:
        application_status = "degraded"
        database_status = "disconnected"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": application_status,
        "service": "TransitOps API",
        "database": database_status,
        "timestamp": datetime.now(UTC).isoformat(),
    }

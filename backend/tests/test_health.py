from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.endpoints import health


def test_health_check_when_database_is_connected(
    client: TestClient,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        health,
        "check_database_connection",
        lambda: None,
    )

    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"
    assert body["service"] == "TransitOps API"
    assert body["database"] == "connected"
    assert "timestamp" in body


def test_health_check_when_database_is_unavailable(
    client: TestClient,
    monkeypatch: MonkeyPatch,
) -> None:
    def unavailable_database() -> None:
        raise SQLAlchemyError("Database unavailable")

    monkeypatch.setattr(
        health,
        "check_database_connection",
        unavailable_database,
    )

    response = client.get("/api/v1/health")

    assert response.status_code == 503

    body = response.json()

    assert body["status"] == "degraded"
    assert body["database"] == "disconnected"

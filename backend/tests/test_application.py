from fastapi.testclient import TestClient


def test_application_info(client: TestClient) -> None:
    response = client.get("/api/v1/info")

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "TransitOps API"
    assert body["version"] == "0.1.0"
    assert body["environment"] == "local"


def test_unknown_route_returns_standard_error(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/unknown")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "http_error",
            "message": "Not Found",
            "details": None,
        }
    }


def test_security_headers(client: TestClient) -> None:
    response = client.get("/api/v1/info")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == (
        "geolocation=(), microphone=(), camera=()"
    )

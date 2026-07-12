from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.role import RoleName
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository

TEST_PASSWORD = "Secure-test-password-123!"


def create_test_user(
    session: Session,
    *,
    role_name: RoleName,
    is_active: bool = True,
) -> User:
    role = RoleRepository(session).get_by_name(role_name)
    assert role is not None

    user = UserRepository(session).create(
        email=f"{role_name.value}-{uuid4()}@example.com",
        full_name="Test User",
        password_hash=hash_password(TEST_PASSWORD),
        role=role,
        is_active=is_active,
    )
    session.commit()

    return user


def login(client: TestClient, user: User) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def authorization_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_valid_login_and_current_user(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    user = create_test_user(
        db_session,
        role_name=RoleName.DISPATCHER,
    )

    token = login(auth_client, user)
    response = auth_client.get(
        "/api/v1/auth/me",
        headers=authorization_header(token),
    )

    assert response.status_code == 200
    assert response.json()["email"] == user.email
    assert response.json()["role"]["name"] == "dispatcher"
    assert "password_hash" not in response.json()


def test_login_uses_generic_failure_response(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    user = create_test_user(
        db_session,
        role_name=RoleName.DISPATCHER,
    )

    wrong_password = auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "incorrect-password",
        },
    )
    unknown_email = auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "incorrect-password",
        },
    )

    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_disabled_user_cannot_login(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    user = create_test_user(
        db_session,
        role_name=RoleName.DISPATCHER,
        is_active=False,
    )

    response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401


def test_invalid_bearer_token_is_rejected(
    auth_client: TestClient,
) -> None:
    response = auth_client.get(
        "/api/v1/auth/me",
        headers=authorization_header("not-a-valid-jwt"),
    )

    assert response.status_code == 401


def test_non_admin_cannot_manage_users(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    dispatcher = create_test_user(
        db_session,
        role_name=RoleName.DISPATCHER,
    )
    token = login(auth_client, dispatcher)

    response = auth_client.get(
        "/api/v1/users",
        headers=authorization_header(token),
    )

    assert response.status_code == 403


def test_admin_can_create_user(
    auth_client: TestClient,
    db_session: Session,
) -> None:
    admin = create_test_user(
        db_session,
        role_name=RoleName.ADMIN,
    )
    token = login(auth_client, admin)

    response = auth_client.post(
        "/api/v1/users",
        headers=authorization_header(token),
        json={
            "email": " NEW.USER@EXAMPLE.COM ",
            "full_name": "New User",
            "password": TEST_PASSWORD,
            "role": "safety_officer",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new.user@example.com"
    assert response.json()["role"]["name"] == "safety_officer"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

import pytest
from fastapi import HTTPException

from app.api.dependencies import RoleChecker
from app.models.role import Role, RoleName
from app.models.user import User


def build_user(role_name: RoleName) -> User:
    role = Role(
        name=role_name,
        display_name=role_name.value,
        description="Test role",
    )

    return User(
        email=f"{role_name.value}@example.com",
        full_name="Test User",
        password_hash="test-hash",
        is_active=True,
        role=role,
    )


def test_allowed_role_is_accepted() -> None:
    user = build_user(RoleName.DISPATCHER)
    checker = RoleChecker(RoleName.DISPATCHER)

    assert checker(user) is user


def test_admin_can_access_any_role_protected_route() -> None:
    user = build_user(RoleName.ADMIN)
    checker = RoleChecker(RoleName.DISPATCHER)

    assert checker(user) is user


def test_disallowed_role_is_rejected() -> None:
    user = build_user(RoleName.FINANCIAL_ANALYST)
    checker = RoleChecker(RoleName.DISPATCHER)

    with pytest.raises(HTTPException) as error:
        checker(user)

    assert error.value.status_code == 403


def test_role_checker_requires_at_least_one_role() -> None:
    with pytest.raises(ValueError):
        RoleChecker()

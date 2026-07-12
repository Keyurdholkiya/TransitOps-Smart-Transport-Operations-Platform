from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.tokens import decode_access_token
from app.db.session import get_db_session
from app.models.role import RoleName
from app.models.user import User
from app.repositories.user_repository import UserRepository

DatabaseSession = Annotated[Session, Depends(get_db_session)]

_bearer_scheme = HTTPBearer(
    auto_error=False,
    bearerFormat="JWT",
)


def _authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(_bearer_scheme),
]


def get_current_user(
    credentials: BearerCredentials,
    session: DatabaseSession,
) -> User:
    if credentials is None:
        raise _authentication_error()

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")

        if not isinstance(subject, str):
            raise _authentication_error()

        user_id = UUID(subject)
    except (InvalidTokenError, ValueError) as error:
        raise _authentication_error() from error

    user = UserRepository(session).get_by_id(user_id)

    if user is None or not user.is_active:
        raise _authentication_error()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


class RoleChecker:
    def __init__(self, *allowed_roles: RoleName) -> None:
        if not allowed_roles:
            raise ValueError("At least one allowed role is required.")

        self.allowed_roles = frozenset(allowed_roles)

    def __call__(self, current_user: CurrentUser) -> User:
        current_role = current_user.role.name

        if current_role == RoleName.ADMIN:
            return current_user

        if current_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user


def require_roles(*allowed_roles: RoleName) -> RoleChecker:
    return RoleChecker(*allowed_roles)

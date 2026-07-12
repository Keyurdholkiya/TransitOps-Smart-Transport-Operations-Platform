from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models.role import RoleName
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService


def require_admin(current_user: CurrentUser) -> User:
    if current_user.role.name != RoleName.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )

    return current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(require_admin)],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    session: DatabaseSession,
) -> User:
    return UserService(session).create_user(data)


@router.get(
    "",
    response_model=list[UserResponse],
)
def list_users(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[User]:
    return UserService(session).list_users(
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    session: DatabaseSession,
) -> User:
    return UserService(session).get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    session: DatabaseSession,
) -> User:
    return UserService(session).update_user(user_id, data)

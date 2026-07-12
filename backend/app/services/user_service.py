from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailAlreadyExistsError,
    RoleNotFoundError,
    UserNotFoundError,
)
from app.core.security import hash_password
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.role_repository = RoleRepository(session)

    def create_user(self, data: UserCreate) -> User:
        if self.user_repository.get_by_email(str(data.email)) is not None:
            raise EmailAlreadyExistsError

        role = self.role_repository.get_by_name(data.role)

        if role is None:
            raise RoleNotFoundError

        try:
            user = self.user_repository.create(
                email=str(data.email),
                full_name=data.full_name,
                password_hash=hash_password(data.password.get_secret_value()),
                role=role,
            )
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise EmailAlreadyExistsError from error

        return user

    def get_user(self, user_id: UUID) -> User:
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError

        return user

    def list_users(
        self,
        *,
        offset: int,
        limit: int,
    ) -> list[User]:
        return self.user_repository.list_users(
            offset=offset,
            limit=limit,
        )

    def update_user(
        self,
        user_id: UUID,
        data: UserUpdate,
    ) -> User:
        user = self.get_user(user_id)

        if data.email is not None:
            existing_user = self.user_repository.get_by_email(str(data.email))

            if existing_user is not None and existing_user.id != user.id:
                raise EmailAlreadyExistsError

            user.email = str(data.email)

        if data.full_name is not None:
            user.full_name = data.full_name

        if data.role is not None:
            role = self.role_repository.get_by_name(data.role)

            if role is None:
                raise RoleNotFoundError

            user.role = role

        if data.is_active is not None:
            user.is_active = data.is_active

        try:
            self.user_repository.save(user)
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise EmailAlreadyExistsError from error

        return user

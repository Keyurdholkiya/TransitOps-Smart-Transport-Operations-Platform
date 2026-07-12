from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.role import Role
from app.models.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        statement = (
            select(User).options(joinedload(User.role)).where(User.id == user_id)
        )

        return self.session.scalar(statement)

    def get_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()

        statement = (
            select(User)
            .options(joinedload(User.role))
            .where(User.email == normalized_email)
        )

        return self.session.scalar(statement)

    def list_users(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[User]:
        statement = (
            select(User)
            .options(joinedload(User.role))
            .order_by(User.created_at.desc(), User.id)
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())

    def create(
        self,
        *,
        email: str,
        full_name: str,
        password_hash: str,
        role: Role,
        is_active: bool = True,
    ) -> User:
        user = User(
            email=email.strip().lower(),
            full_name=" ".join(full_name.split()),
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )

        self.session.add(user)
        self.session.flush()

        return user

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role, RoleName


class RoleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_name(self, name: RoleName) -> Role | None:
        statement = select(Role).where(Role.name == name)
        return self.session.scalar(statement)

    def list_roles(self) -> list[Role]:
        statement = select(Role).order_by(Role.id)
        return list(self.session.scalars(statement).all())

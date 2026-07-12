from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.role import Role, RoleName
from app.models.user import User
from app.repositories.user_repository import UserRepository

ROLE_DEFINITIONS = {
    RoleName.ADMIN: (
        "Admin",
        "Full access, including user and role management.",
    ),
    RoleName.FLEET_MANAGER: (
        "Fleet Manager",
        "Manages vehicles, trips, maintenance and operational dashboards.",
    ),
    RoleName.DISPATCHER: (
        "Dispatcher",
        "Views resources and manages trip dispatch operations.",
    ),
    RoleName.SAFETY_OFFICER: (
        "Safety Officer",
        "Manages drivers, licences and safety information.",
    ),
    RoleName.FINANCIAL_ANALYST: (
        "Financial Analyst",
        "Manages fuel, expenses and financial reports.",
    ),
}


def seed_roles(session: Session) -> dict[RoleName, Role]:
    existing_roles = {role.name: role for role in session.scalars(select(Role)).all()}

    for role_name, (display_name, description) in ROLE_DEFINITIONS.items():
        role = existing_roles.get(role_name)

        if role is None:
            role = Role(
                name=role_name,
                display_name=display_name,
                description=description,
            )
            session.add(role)
            existing_roles[role_name] = role
        else:
            role.display_name = display_name
            role.description = description

    session.flush()
    return existing_roles


def seed_initial_admin(
    session: Session,
    roles: dict[RoleName, Role],
) -> User:
    if settings.initial_admin_email is None:
        raise RuntimeError("INITIAL_ADMIN_EMAIL is not configured.")

    if settings.initial_admin_password is None:
        raise RuntimeError("INITIAL_ADMIN_PASSWORD is not configured.")

    password = settings.initial_admin_password.get_secret_value()

    if not 12 <= len(password) <= 128:
        raise RuntimeError(
            "INITIAL_ADMIN_PASSWORD must contain between 12 and 128 characters."
        )

    repository = UserRepository(session)
    email = str(settings.initial_admin_email)
    existing_user = repository.get_by_email(email)

    if existing_user is not None:
        if existing_user.role.name != RoleName.ADMIN:
            raise RuntimeError(
                "The configured admin email belongs to a non-admin user."
            )

        if not existing_user.is_active:
            raise RuntimeError("The configured admin user is disabled.")

        return existing_user

    return repository.create(
        email=email,
        full_name=settings.initial_admin_full_name,
        password_hash=hash_password(password),
        role=roles[RoleName.ADMIN],
    )


def main() -> None:
    with SessionLocal() as session:
        try:
            roles = seed_roles(session)
            admin = seed_initial_admin(session, roles)
            session.commit()
        except Exception:
            session.rollback()
            raise

    print(f"Seeded {len(roles)} roles.")
    print(f"Initial admin ready: {admin.email}")


if __name__ == "__main__":
    main()

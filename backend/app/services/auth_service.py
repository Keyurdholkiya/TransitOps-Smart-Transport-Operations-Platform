from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError
from app.core.security import hash_password, verify_password
from app.core.tokens import create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

_DUMMY_PASSWORD_HASH = hash_password(
    "TransitOps-dummy-password-used-only-for-timing-protection"
)


class AuthService:
    def __init__(self, session: Session) -> None:
        self.user_repository = UserRepository(session)

    def authenticate(
        self,
        *,
        email: str,
        password: str,
    ) -> User:
        user = self.user_repository.get_by_email(email)

        stored_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
        password_is_valid = verify_password(password, stored_hash)

        if user is None or not password_is_valid or not user.is_active:
            raise InvalidCredentialsError

        return user

    def login(
        self,
        *,
        email: str,
        password: str,
    ) -> tuple[User, str]:
        user = self.authenticate(
            email=email,
            password=password,
        )
        access_token = create_access_token(user.id)

        return user, access_token

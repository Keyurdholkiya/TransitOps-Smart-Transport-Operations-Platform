from fastapi import APIRouter

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    credentials: LoginRequest,
    session: DatabaseSession,
) -> TokenResponse:
    _, access_token = AuthService(session).login(
        email=str(credentials.email),
        password=credentials.password.get_secret_value(),
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(current_user: CurrentUser) -> User:
    return current_user

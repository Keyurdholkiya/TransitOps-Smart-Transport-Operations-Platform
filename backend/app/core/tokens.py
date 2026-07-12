from datetime import timedelta
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from app.core.config import settings
from app.core.time import utc_now

ACCESS_TOKEN_TYPE = "access"

_REQUIRED_ACCESS_TOKEN_CLAIMS = [
    "sub",
    "type",
    "iat",
    "nbf",
    "exp",
    "iss",
    "aud",
]


def create_access_token(
    subject: UUID | str,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    issued_at = utc_now()
    lifetime = (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload = {
        "sub": str(subject),
        "type": ACCESS_TOKEN_TYPE,
        "iat": issued_at,
        "nbf": issued_at,
        "exp": issued_at + lifetime,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, object]:
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={"require": _REQUIRED_ACCESS_TOKEN_CLAIMS},
    )

    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise InvalidTokenError("Invalid token type.")

    return payload

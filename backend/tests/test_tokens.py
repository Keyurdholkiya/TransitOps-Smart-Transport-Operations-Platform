from datetime import timedelta
from uuid import uuid4

import pytest
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.tokens import create_access_token, decode_access_token


def test_create_and_decode_access_token() -> None:
    user_id = uuid4()

    token = create_access_token(user_id)
    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(
        uuid4(),
        expires_delta=timedelta(minutes=-1),
    )

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)


def test_tampered_access_token_is_rejected() -> None:
    token = create_access_token(uuid4())
    header, payload, signature = token.split(".")

    replacement = "A" if payload[0] != "A" else "B"
    tampered_payload = replacement + payload[1:]
    tampered_token = ".".join((header, tampered_payload, signature))

    with pytest.raises(InvalidTokenError):
        decode_access_token(tampered_token)

from app.core.security import hash_password, verify_password


def test_hash_and_verify_password() -> None:
    plain_password = "A-secure-password-123!"
    password_hash = hash_password(plain_password)

    assert password_hash != plain_password
    assert password_hash.startswith("$argon2")
    assert verify_password(plain_password, password_hash)
    assert not verify_password("incorrect-password", password_hash)


def test_same_password_produces_different_hashes() -> None:
    plain_password = "A-secure-password-123!"

    first_hash = hash_password(plain_password)
    second_hash = hash_password(plain_password)

    assert first_hash != second_hash

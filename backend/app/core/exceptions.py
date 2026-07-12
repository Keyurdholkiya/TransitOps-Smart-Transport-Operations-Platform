from typing import Any


class AppException(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)

        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class InvalidCredentialsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            code="invalid_credentials",
            message="Invalid email or password.",
        )

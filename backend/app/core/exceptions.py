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


class UserNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            code="user_not_found",
            message="User not found.",
        )


class RoleNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=400,
            code="invalid_role",
            message="The selected role does not exist.",
        )


class EmailAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            code="email_already_exists",
            message="A user with this email already exists.",
        )

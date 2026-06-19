from enum import StrEnum
from fastapi import status

class ErrorType(StrEnum):
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    INTERNAL_ERROR = "internal_error"
    TOKEN_EXPIRED = "token_expired"
    INVALID_TOKEN = "invalid_token"

class AppException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_type: ErrorType = ErrorType.INTERNAL_ERROR
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class ValidationException(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_type = ErrorType.VALIDATION_ERROR
    message = "Validation failed"


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_type = ErrorType.NOT_FOUND
    message = "Resource not found"


class AlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_type = ErrorType.ALREADY_EXISTS
    message = "Resource already exists"


class UnauthorizedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_type = ErrorType.UNAUTHORIZED
    message = "Authentication required"


class ForbiddenException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_type = ErrorType.FORBIDDEN
    message = "You do not have permission to perform this action"
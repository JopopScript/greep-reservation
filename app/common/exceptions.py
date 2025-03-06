from enum import Enum

from starlette.authentication import AuthenticationError


class ErrorCode(str, Enum):
    NOT_EXIST_RESOURCE = "NOT_EXIST_RESOURCE"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    INVALID_STATE = "INVALID_STATE"
    NO_AUTHENTICATE = "NO_AUTHENTICATE"
    ACCESS_DENIED = "ACCESS_DENIED"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class CustomException(Exception):
    def __init__(self, message: str, code: ErrorCode):
        self.__message = message
        self.__code: ErrorCode = code
        super().__init__(message)

    def code(self) -> str | None:
        return None if self.__code is None else self.__code.value

    def message(self) -> str:
        return self.__message


class AuthenticateException(CustomException, AuthenticationError):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.NO_AUTHENTICATE):
        super().__init__(message, code)


class AuthorizationException(CustomException, AuthenticationError):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.ACCESS_DENIED):
        super().__init__(message, code)


class BusinessException(CustomException):
    def __init__(self, message: str, code: ErrorCode):
        super().__init__(message, code)


class InternalServerException(CustomException):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR):
        super().__init__(message, code)


class NoResourceException(CustomException):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.NOT_EXIST_RESOURCE):
        super().__init__(message, code)

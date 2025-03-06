from enum import Enum

from starlette.authentication import (
    AuthenticationError
)


class ErrorCode(str, Enum):
    NOT_EXIST_RESOURCE = 'NOT_EXIST_RESOURCE'
    INVALID_ARGUMENT = 'INVALID_ARGUMENT'
    INVALID_STATE = 'INVALID_STATE'
    NO_AUTHENTICATE = 'NO_AUTHENTICATE'
    ACCESS_DENIED = 'ACCESS_DENIED'
    INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'


class CustomException(Exception):
    def __init__(self, message: str, code: ErrorCode):
        self.message = message
        self.code: ErrorCode = code
        super().__init__(self.message)


class AuthenticateException(CustomException, AuthenticationError):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.NO_AUTHENTICATE):
        self.message = message
        super().__init__(self.message, code)


class AuthorizationException(CustomException, AuthenticationError):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.ACCESS_DENIED):
        self.message = message
        super().__init__(self.message, code)


class BusinessException(CustomException):
    def __init__(self, message: str, code: ErrorCode):
        self.message = message
        super().__init__(self.message, code)


class InternalServerException(CustomException):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR):
        self.message = message
        super().__init__(self.message, code)


class NoResourceException(CustomException):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.NOT_EXIST_RESOURCE):
        self.message = message
        super().__init__(self.message, code)

from uuid import UUID

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
    UnauthenticatedUser,
)
from starlette.requests import HTTPConnection
from starlette.responses import Response

from app.common.authentication import Authentication
from app.common.enviroment import env
from app.common.exception_handler import (
    error_content,
    DEFAULT_ERROR_RESPONSE_CONTENTS,
)
from app.common.exceptions import AuthorizationException, AuthenticateException
from app.common.jwt_token import jwt_token_util
from app.service.models.role import Role


class BearerTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, request) -> tuple[AuthCredentials, BaseUser]:
        path = request.url.path
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if any(path.startswith(url) for url in env.AUTHENTICATE_URL_PREFIX):
            user = jwt_token_util.verify_access_token(token)
            return user.auth_credentials(), user
        elif any(path.startswith(url) for url in env.ADMIN_URL_PREFIX):
            user: Authentication = jwt_token_util.verify_access_token(token)
            if user.role is not Role.ADMIN:
                raise AuthorizationException("access denied")
            return user.auth_credentials(), user
        else:
            return AuthCredentials(), UnauthenticatedUser()


def auth_error_handler(_: HTTPConnection, error: AuthenticationError) -> Response:
    if isinstance(error, AuthenticateException):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_content(error),
        )
    elif isinstance(error, AuthorizationException):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content=error_content(error)
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=DEFAULT_ERROR_RESPONSE_CONTENTS,
        )


def authentication(request: Request) -> Authentication:
    return request.user


def account_id(request: Request) -> UUID:
    return request.user.account_id

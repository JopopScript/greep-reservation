from uuid import UUID

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.authentication import AuthenticationBackend

from app.common.authentication import Authentication
from app.common.enviroment import env
from app.common.exception_handler import toResponseContent
from app.common.exceptions import AuthorizationException, AuthenticateException
from app.common.jwt_token import jwt_token_util
from app.service.models.role import Role


class BearerTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        path = request.url.path
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header.replace('Bearer ', '')

        if any(path.startswith(url) for url in env.AUTHENTICATE_URL_PREFIX):
            try:
                user = jwt_token_util.verify_access_token(token)
                return authorization_header, user
            except AuthenticateException as e:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=toResponseContent(e),
                )
        elif any(path.startswith(url) for url in env.ADMIN_URL_PREFIX):
            try:
                user: Authentication = jwt_token_util.verify_access_token(token)
                if user.role is not Role.ADMIN:
                    raise AuthorizationException('access denied')
                return authorization_header, user
            except (AuthenticateException, AuthorizationException) as e:
                status_code = status.HTTP_401_UNAUTHORIZED \
                    if isinstance(e, AuthenticateException) \
                    else status.HTTP_403_FORBIDDEN
                return JSONResponse(
                    status_code=status_code,
                    content=toResponseContent(e),
                )
        return authorization_header, Authentication.anonymous()


def authentication(request: Request) -> Authentication:
    return request.user


def account_id(request: Request) -> UUID:
    return request.user.account_id

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.common.enviroment import env
from app.common.exception_handler import toResponseContent
from app.common.exceptions import AuthorizationException, AuthenticateException
from app.common.jwt_token import Authentication, jwt_token_util
from app.service.models.role import Role


# TODO 추후에 시간되면 인증전용 midelware로 변경
#  from starlette.middleware.authentication import AuthenticationMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if any(path.startswith(url) for url in env.AUTHENTICATE_URL_PREFIX):
            try:
                request.state.auth = jwt_token_util.verify_access_token(token)
            except AuthenticateException as e:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content=toResponseContent(e),
                )
        elif any(path.startswith(url) for url in env.ADMIN_URL_PREFIX):
            try:
                auth: Authentication = jwt_token_util.verify_access_token(token)
                if auth.role is not Role.ADMIN:
                    raise AuthorizationException('access denied')
                request.state.auth = auth
            except (AuthenticateException, AuthorizationException) as e:
                status_code = status.HTTP_401_UNAUTHORIZED \
                    if isinstance(e, AuthenticateException) \
                    else status.HTTP_403_FORBIDDEN
                return JSONResponse(
                    status_code=status_code,
                    content=toResponseContent(e),
                )
        response = await call_next(request)
        return response

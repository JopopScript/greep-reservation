from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware

from app.api.api_router import api_router
from app.common.auth_middleware import BearerTokenAuthBackend, auth_error_handler
from app.common.enviroment import env
from app.common.exception_handler import exception_handle

app: FastAPI = FastAPI(
    title='exam schedule reservation system',
    docs_url=env.DOCS_URL,
)

exception_handle(app)

app.add_middleware(
    AuthenticationMiddleware,
    backend=BearerTokenAuthBackend(),
    on_error=auth_error_handler
)

app.include_router(api_router)

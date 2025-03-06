from fastapi import FastAPI

from app.api.api_router import api_router
from app.common.auth_middleware import AuthMiddleware
from app.common.enviroment import env
from app.common.exception_handler import exception_handle

app: FastAPI = FastAPI(
    title='exam schedule reservation system',
    docs_url=env.DOCS_URL,
)

exception_handle(app)

app.add_middleware(AuthMiddleware)

app.include_router(api_router)

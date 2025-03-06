from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.common.exceptions import (
    AuthenticateException,
    InternalServerException,
    CustomException,
    BusinessException,
    AuthorizationException,
    NoResourceException,
)

DEFAULT_CODE = "NONE"
DEFAULT_ERROR_MESSAGE = "알 수 없는 에러가 발생했습니다. 관리자에게 문의해주세요."

DEFAULT_ERROR_RESPONSE_CONTENTS = {
    "code": DEFAULT_CODE,
    "message": DEFAULT_ERROR_MESSAGE,
}


def error_content(e: CustomException) -> dict:
    return {
        "code": DEFAULT_CODE if e.code() is None else e.code(),
        "message": DEFAULT_ERROR_MESSAGE if e.message() is None else e.message(),
    }


def exception_handle(app: FastAPI):
    @app.exception_handler(AuthenticateException)
    async def authenticate_exception_handle(
        _: Request, exception: AuthenticateException
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_content(exception),
        )

    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handle(
        _: Request, exception: AuthorizationException
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_content(exception),
        )

    @app.exception_handler(BusinessException)
    async def business_exception_handle(_: Request, exception: BusinessException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_content(exception),
        )

    @app.exception_handler(NoResourceException)
    async def no_resource_exception_handle(_: Request, exception: NoResourceException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_content(exception),
        )

    @app.exception_handler(InternalServerException)
    async def internal_server_exception_handle(
        _: Request, exception: InternalServerException
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_content(exception),
        )

    @app.exception_handler(CustomException)
    async def custom_exception_handle(_: Request, exception: CustomException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_content(exception),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handle(_: Request, exception: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=DEFAULT_ERROR_RESPONSE_CONTENTS,
        )

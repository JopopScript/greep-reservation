from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.common.exceptions import AuthenticateException, ErrorCode, InternalServerException, CustomException, \
    BusinessException, AuthorizationException, NoResourceException


def toResponseContent(e: CustomException) -> dict:
    return {
        'code': __code_or_default(e.code),
        'message': __message_or_default(e.message),
    }


DEFAULT_ERROR_MESSAGE = '알 수 없는 에러가 발생했습니다. 관리자에게 문의해주세요.'
DEFAULT_CODE = 'NONE'


def __message_or_default(message: str):
    return DEFAULT_ERROR_MESSAGE if message is None else message


def __code_or_default(error_code: ErrorCode):
    return DEFAULT_CODE if error_code is None else error_code.value


def exception_handle(app: FastAPI):
    @app.exception_handler(AuthenticateException)
    async def authenticate_exception_handle(request: Request, exception: AuthenticateException):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=toResponseContent(exception),
        )

    @app.exception_handler(AuthorizationException)
    async def authenticate_exception_handle(request: Request, exception: AuthorizationException):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=toResponseContent(exception),
        )

    @app.exception_handler(BusinessException)
    async def business_exception_handle(request: Request, exception: BusinessException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=toResponseContent(exception),
        )

    @app.exception_handler(NoResourceException)
    async def business_exception_handle(request: Request, exception: NoResourceException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=toResponseContent(exception),
        )

    @app.exception_handler(InternalServerException)
    async def internal_server_exception_handle(request: Request, exception: InternalServerException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=toResponseContent(exception),
        )

    @app.exception_handler(CustomException)
    async def custom_exception_handle(request: Request, exception: CustomException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=toResponseContent(exception),
        )

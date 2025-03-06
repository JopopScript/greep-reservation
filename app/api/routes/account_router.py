from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.routes.dto.account_dto import AccountResponse, AccountCreateRequest
from app.common.jwt_token import jwt_token_util, Authentication
from app.dependencies import account_service
from app.service.account_service import AccountService

router = APIRouter(tags=['accounts'])


@router.post('/accounts', response_model=AccountResponse)
async def create_account(
        request: AccountCreateRequest,
        service: AccountService = Depends(account_service)
) -> AccountResponse:
    account = await service.create(request.nickname, request.role)
    return AccountResponse.fromAccount(account)


@router.get('/accounts/{account_id}', response_model=AccountResponse)
async def get_account(
        account_id: UUID,
        service: AccountService = Depends(account_service)
) -> AccountResponse:
    account = await service.get_or_raise(account_id)
    return AccountResponse.fromAccount(account)


class AccessTokenResponse(BaseModel):
    access_token: str


# 테스트 인증키 발급을 위한 api
@router.post('/token/{account_id}', response_model=AccessTokenResponse)
async def get_account(
        account_id: UUID,
        service: AccountService = Depends(account_service)
) -> AccessTokenResponse:
    account = await service.get_or_raise(account_id)
    token = jwt_token_util.create_access_token(
        Authentication(account_id=account.id, role=account.role))
    return AccessTokenResponse(access_token=token)

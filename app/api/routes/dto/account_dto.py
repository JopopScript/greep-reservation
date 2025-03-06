from uuid import UUID

from pydantic import BaseModel

from app.service.models.role import Role
from app.storage.models.account import Account


class AccountCreateRequest(BaseModel):
    nickname: str
    role: Role


class AccountResponse(BaseModel):
    id: UUID
    nickname: str
    role: Role

    @staticmethod
    def from_account(account: Account) -> "AccountResponse":
        return AccountResponse(
            id=account.id,
            nickname=account.nickname,
            role=account.role,
        )


class ProfileResponse(BaseModel):
    id: UUID
    nickname: str

    @staticmethod
    def from_account(account: Account) -> "ProfileResponse":
        return ProfileResponse(
            id=account.id,
            nickname=account.nickname,
        )

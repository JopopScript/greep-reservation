from typing import Optional
from uuid import uuid4, UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.exceptions import NoResourceException
from app.service.models.role import Role
from app.storage.account_repository import AccountRepository
from app.storage.models.account import Account


class AccountService:
    def __init__(self, repository: AccountRepository, sess: AsyncSession):
        self.repository = repository
        self.sess = sess

    async def create(self, nickname: str, role: Role) -> Account:
        return await self.repository.save(
            Account(id=uuid4(), nickname=nickname, role=role)
        )

    async def get(self, account_id: UUID) -> Optional[Account]:
        return await self.repository.find_by_id(account_id)

    async def get_or_raise(self, account_id: UUID) -> Account:
        account = await self.get(account_id)
        if account is None:
            raise NoResourceException(f"not exist account. account_id: '{account_id}'")
        return account

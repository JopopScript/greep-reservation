from typing import Optional
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.storage.models.account import Account


class AccountRepository:
    def __init__(self, sess: AsyncSession):
        self.sess = sess

    async def save(self, account: Account) -> Account:
        self.sess.add(account)
        await self.sess.flush()
        return account

    async def find_by_id(self, account_id: UUID) -> Optional[Account]:
        return await self.sess.get(Account, account_id)

from typing import AsyncGenerator
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.enviroment import env
from app.main import app
from app.service.models.role import Role
from app.storage.models.account import Account
from app.storage.models.schedule import Schedule
from app.storage.models.schedule_slot import ScheduleSlot

async_engine = create_async_engine(str(env.DATABASE_URL), echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

init_users = [
    {
        "id": UUID("00000000-0000-4000-0000-000000000000"),
        "nickname": "admin",
        "role": Role.ADMIN,
    },
    {
        "id": UUID("00000000-0000-4000-0000-000000000001"),
        "nickname": "first_customer",
        "role": Role.CUSTOMER,
    },
    {
        "id": UUID("00000000-0000-4000-0000-000000000002"),
        "nickname": "second_customer",
        "role": Role.CUSTOMER,
    },
]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


async def init_db(session: AsyncSession) -> None:
    stmt = select(Account.id).where(Account.id.in_([user["id"] for user in init_users]))
    existing_user_ids = (await session.exec(stmt)).all()

    for user in init_users:
        if user["id"] not in existing_user_ids:
            account = Account(
                id=user["id"], nickname=user["nickname"], role=user["role"]
            )
            session.add(account)
    await session.commit()


@pytest.fixture(scope="session", autouse=True)
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        await init_db(session)
        yield session


@pytest.fixture(scope="class", autouse=True)
async def tear_down_db(db: AsyncSession) -> None:
    await db.exec(delete(ScheduleSlot))
    await db.exec(delete(Schedule))
    await db.commit()


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as c:
        yield c


class AccountToken:
    def __init__(self, id: UUID, nickname: str, token: dict[str, str]):
        self.id: UUID = id
        self.nickname: str = nickname
        self.token: dict[str, str] = token


class Tokens:
    def __init__(self, admin: AccountToken, first: AccountToken, second: AccountToken):
        self.admin: AccountToken = admin
        self.first: AccountToken = first
        self.second: AccountToken = second

    def admin_token(self) -> dict[str, str]:
        return self.admin.token

    def first_token(self) -> dict[str, str]:
        return self.first.token

    def second_token(self) -> dict[str, str]:
        return self.second.token

    def first_profile(self) -> dict[str, str]:
        return self.__profile(self.first)

    def second_profile(self) -> dict[str, str]:
        return self.__profile(self.second)

    @staticmethod
    def __profile(account: AccountToken):
        return {"id": str(account.id), "nickname": account.nickname}


@pytest.fixture(scope="session")
async def tokens(client: AsyncClient, db: AsyncSession) -> Tokens:
    return Tokens(
        *[
            AccountToken(
                user["id"],
                user["nickname"],
                await token_headers(client, str(user["id"])),
            )
            for user in init_users
        ]
    )


@pytest.mark.anyio
async def token_headers(client: AsyncClient, account_id: str) -> dict[str, str]:
    response = await client.post(f"/token/{account_id}")
    tokens = response.json()
    if "access_token" in tokens:
        return {"Authorization": f"Bearer {tokens['access_token']}"}
    else:
        raise ValueError("Access token not found in response.")

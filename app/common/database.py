import logging
from contextlib import asynccontextmanager

from app.common.enviroment import env
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

if env.is_local():
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
__async_engine = create_async_engine(
    str(env.DATABASE_URL),
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=__async_engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def __get_session():
    async with AsyncSessionLocal() as sess:
        try:
            yield sess
            await sess.commit()
        except Exception:
            await sess.rollback()
            raise


async def session():
    async with __get_session() as sess:
        yield sess

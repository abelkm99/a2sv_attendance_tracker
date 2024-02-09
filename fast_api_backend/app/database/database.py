from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

# from app.utils.logger import sqlalchemy_logger as logger
from config import MySettings

async_engine = create_async_engine(
    url=MySettings.DATABASE_URL,
    future=True,
    # echo=True,
    pool_size=20,
    max_overflow=20,
)


AsyncSessionFactory: async_sessionmaker = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session


async def get_db_router() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session

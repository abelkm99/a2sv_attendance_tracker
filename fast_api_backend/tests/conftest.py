from asyncpg.pool import asyncio
import pytest
import pytest_asyncio
from app.database.base import Base
from app.database.database import async_engine as engine, get_db
from httpx import AsyncClient
from main import app

# app = create_app(config)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def reset_database():
    async with engine.begin() as conn:
        print("*" * 10, "resetting database", "*" * 10)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    async with get_db() as session:
        try:
            yield session
            await session.close()
        except Exception:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

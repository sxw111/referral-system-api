import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import fakeredis
import pytest_asyncio
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.auth.models import User
from app.auth.service import get_current_user
from app.config import settings
from app.database.core import Base, get_db
from app.main import app

DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
    f"{settings.TEST_DB_NAME}"
)

async_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
async_test_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    async_engine, expire_on_commit=False
)


# reset the database before each test
@pytest_asyncio.fixture(autouse=True)
async def reset_db() -> None:
    """Reset the database."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# Override the database connection to use the test database
async def get_database_override() -> AsyncGenerator[AsyncSession, Any]:
    """Return the database connection for testing."""
    async with async_test_session() as session:
        yield session


@pytest_asyncio.fixture()
async def test_db() -> AsyncGenerator[AsyncSession, Any]:
    """Fixture to yield a database connection for testing."""
    async with async_test_session() as session:
        yield session


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, Any]:
    """Fixture to yield a test client for the app."""
    app.dependency_overrides[get_db] = get_database_override
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver/api/v1",
        headers={"Content-Type": "application/json"},
        timeout=10,
    ) as client:
        yield client
    app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
def setup_cache():
    fake_redis = fakeredis.FakeStrictRedis()
    FastAPICache.init(RedisBackend(fake_redis), prefix="fastapi-cache")
    yield
    FastAPICache.clear()


@pytest_asyncio.fixture(scope="function")
async def current_user(test_db: AsyncSession):
    test_user = User(id=2, email="test@example.com", password="hashedpassword")
    test_db.add(test_user)
    await test_db.commit()
    await test_db.refresh(test_user)

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    yield test_user

    await test_db.delete(test_user)
    await test_db.commit()

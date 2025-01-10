import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from tests.models import Base, DATABASE_URL


@pytest_asyncio.fixture
def async_engine():
    yield create_async_engine(
        DATABASE_URL.set(drivername='timescaledb+asyncpg'),
		echo=True
    )


@pytest_asyncio.fixture
async def async_session(async_engine):
    async with AsyncSession(async_engine) as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup(async_engine):
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

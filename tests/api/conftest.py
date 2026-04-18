from typing import AsyncGenerator, AsyncIterator, Final
from unittest.mock import AsyncMock
from threading import Thread
import os

import pytest
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from dishka import Provider, AsyncContainer, make_async_container, provide, Scope
from dishka.integrations.fastapi import FastapiProvider

from prodik.bootstrap.cli import run_migrations
from prodik.bootstrap.api import create_app
from prodik.infrastructure.config import load_config, Config, APIConfig, PersistenceConfig, ObjectStorageConfig
from prodik.bootstrap.di.providers.application import ApplicationProvider
from prodik.bootstrap.di.providers.connection import S3Provider
from prodik.bootstrap.di.providers.infrastructure import InfrastructureProvider


@pytest.fixture(scope="session")
def test_config() -> Config:
    os.environ['CONFIG'] = "test.config.toml"
    config = load_config()
    return config

@pytest.fixture(scope="session")
async def test_engine(test_config: Config) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(test_config.persistence.url)

    async with engine.begin() as connection:
        await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))

    thread = Thread(target=run_migrations)
    thread.start()
    thread.join()

    yield engine

    await engine.dispose()

@pytest.fixture
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    async with (AsyncSession(test_engine) as session, session.begin()):
        session.commit = AsyncMock() # type: ignore[method-assign]
        yield session
        await session.rollback()

@pytest.fixture
async def test_dishka_container(test_session: AsyncSession, test_config: Config) -> AsyncContainer:
    class TestDishkaProvider(Provider):
        override = True

        @provide(scope=Scope.REQUEST)
        def session(self) -> AsyncSession:
            return test_session

    container = make_async_container(
        FastapiProvider(),
        TestDishkaProvider(),
        ApplicationProvider(),
        InfrastructureProvider(),
        context={
            APIConfig: test_config.api,
            PersistenceConfig: test_config.persistence,
            ObjectStorageConfig: test_config.object_storage,
        },
    )

    return container


@pytest.fixture()
async def test_client() -> AsyncGenerator[AsyncClient]:
    config = load_config()
    app = create_app(config.api)
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test.literally.io"
    ) as client:
        yield client
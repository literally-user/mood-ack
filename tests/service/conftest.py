from typing import AsyncGenerator
from unittest.mock import AsyncMock
import os

import pytest
from faker import Faker
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from dishka import Provider, provide, AsyncContainer, Scope, make_async_container

from tests.service.factories import create_user_info, TestUserInformation

from prodik.bootstrap.api import create_app
from prodik.bootstrap.di.providers.transport import HTTPXClientProvider
from prodik.bootstrap.di.providers.infrastructure import InfrastructureProvider
from prodik.bootstrap.di.providers.application import ApplicationProvider
from prodik.bootstrap.di.providers.connection import S3Provider
from prodik.infrastructure.config import load_config, Config, PersistenceConfig, APIConfig, ObjectStorageConfig, KeyCloakConfig
from prodik.infrastructure.db import start_mapper
from prodik.bootstrap.cli import run_migrations

@pytest.fixture(scope="session", autouse=True)
def startup() -> None:
    os.environ['CONFIG'] = "test.config.toml"
    start_mapper()
    run_migrations()

@pytest.fixture(scope="session")
async def test_config() -> Config:
    config = load_config()
    
    return config

@pytest.fixture
async def test_session(test_config: Config) -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine(test_config.persistence.url)
    async with engine.begin() as conn:
        async with AsyncSession(conn) as session:
            session.commit = AsyncMock() # type: ignore 
            yield session
            await session.rollback()

@pytest.fixture()
async def test_container(
    test_session: AsyncSession,
    test_config: Config
) -> AsyncGenerator[AsyncContainer]:
    class TestConnectionProvider(Provider):
        @provide(scope=Scope.REQUEST)
        async def session(self) -> AsyncGenerator[AsyncSession]:
            yield test_session

    container = make_async_container(
        HTTPXClientProvider(),
        TestConnectionProvider(),
        InfrastructureProvider(),
        ApplicationProvider(),
        FastapiProvider(),
        S3Provider(),
        context={
            ObjectStorageConfig: test_config.object_storage,
            PersistenceConfig: test_config.persistence,
            KeyCloakConfig: test_config.keycloak,
            APIConfig: test_config.api,
        }
    )

    yield container
    await container.close()

@pytest.fixture
async def test_user_info(faker: Faker, test_container: AsyncContainer) -> TestUserInformation:
    return await create_user_info(faker, test_container)


@pytest.fixture
async def test_client(test_config: Config, test_container: AsyncContainer) -> AsyncGenerator[AsyncClient]:
    app = create_app(test_config.api)
    setup_dishka(test_container, app)

    async with AsyncClient(
        base_url="http://test.literally.io",
        transport=ASGITransport(app)
    ) as client:
        yield client
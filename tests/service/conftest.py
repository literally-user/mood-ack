from typing import AsyncGenerator, cast
from unittest.mock import AsyncMock
import os

import pytest
from faker import Faker
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from dishka import Provider, provide, AsyncContainer, Scope, make_async_container

from tests.service.factories import UserFactory, TestUserInformation

from prodik.bootstrap.api import create_app
from prodik.bootstrap.di.providers.transport import HTTPXClientProvider
from prodik.bootstrap.di.providers.infrastructure import InfrastructureProvider
from prodik.bootstrap.di.providers.application import ApplicationProvider
from prodik.bootstrap.di.providers.connection import S3Provider
from prodik.infrastructure.config import load_config, Config, PersistenceConfig, APIConfig, ObjectStorageConfig, KeyCloakConfig
from prodik.infrastructure.db import start_mapper
from prodik.bootstrap.cli import run_migrations
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import UserRepository, UserSessionRepository, LocalAuthorizationRepository
from prodik.application.interfaces.token_manager import AccessTokenManager, RefreshTokenManager

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
async def user_repository(test_container: AsyncContainer) -> UserRepository:
    async with test_container() as container:
        return cast(UserRepository, await container.get(UserRepository))

@pytest.fixture
async def user_session_repository(test_container: AsyncContainer) -> UserSessionRepository:
    async with test_container() as container:
        return cast(UserSessionRepository, await container.get(UserSessionRepository))

@pytest.fixture
async def test_user_factory(faker: Faker, test_container: AsyncContainer) -> UserFactory:
    async with test_container() as container:
        return UserFactory(
            faker,
            await container.get(UserRepository),
            await container.get(RefreshTokenManager),
            await container.get(AccessTokenManager),
            await container.get(UserSessionRepository),
            await container.get(LocalAuthorizationRepository),
            await container.get(PasswordHasher),
            await container.get(APIConfig),
        )

@pytest.fixture
async def test_client(test_config: Config, test_container: AsyncContainer) -> AsyncGenerator[AsyncClient]:
    app = create_app(test_config.api)
    setup_dishka(test_container, app)

    async with AsyncClient(
        base_url="http://test.literally.io",
        transport=ASGITransport(app)
    ) as client:
        yield client
from collections.abc import AsyncIterator

from httpx import AsyncClient
from aioboto3.session import Session as AiobotoSession
from aiobotocore.client import AioBaseClient
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from prodik.infrastructure.config import ObjectStorageConfig, PersistenceConfig


class ConnectionProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, config: PersistenceConfig) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(config.url, future=True)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    async def get_async_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            engine,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def get_async_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

class HTTPXClientProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def client(self) -> AsyncClient:
        async with AsyncClient() as client:
            return client

class S3Provider(Provider):
    @provide(scope=Scope.APP)
    def get_s3_session(self, config: ObjectStorageConfig) -> AiobotoSession:
        return AiobotoSession(
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            region_name=config.region,
        )

    @provide(scope=Scope.REQUEST)
    async def get_s3_client(
        self,
        session: AiobotoSession,
        config: ObjectStorageConfig,
    ) -> AsyncIterator[AioBaseClient]:
        async with session.client(
            "s3",
            endpoint_url=config.url,
        ) as client:
            yield client

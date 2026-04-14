from collections.abc import AsyncIterator

from aioboto3.session import Session as AiobotoSession
from aiobotocore.client import AioBaseClient
from dishka import AnyOf, Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.infrastructure.config import Config


class ConnectionProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, config: Config) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(config.api.persistence, future=True)
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
    ) -> AsyncIterator[AnyOf[AsyncSession, TransactionManager]]:
        async with session_factory() as session:
            yield session


class S3Provider(Provider):
    @provide(scope=Scope.APP)
    def get_s3_session(self, config: Config) -> AiobotoSession:
        return AiobotoSession(
            aws_access_key_id=config.object_storage.access_key,
            aws_secret_access_key=config.object_storage.secret_key,
            region_name=config.object_storage.region,
        )

    @provide(scope=Scope.REQUEST)
    async def get_s3_client(
        self,
        session: AiobotoSession,
        config: Config,
    ) -> AsyncIterator[AioBaseClient]:
        async with session.client(
            "s3",
            endpoint_url=config.object_storage.url,
        ) as client:
            yield client

from dishka import Provider, Scope, WithParents, provide, provide_all
from redis.asyncio import Redis

from prodik.application.interfaces.gateways import CacheGateway
from prodik.infrastructure.config import CacheConfig
from prodik.infrastructure.gateways import CacheGatewayImpl
from prodik.infrastructure.predicting_model import PredictingModelImpl
from prodik.infrastructure.repositories import TaskRepositoryImpl
from prodik.infrastructure.transaction_manager import TransactionManagerImpl


class RawHandleProcessProvider(Provider):
    provides = provide_all(
        WithParents[TaskRepositoryImpl],
        WithParents[PredictingModelImpl],
        WithParents[TransactionManagerImpl],
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.APP)
    def get_gateway(self, config: CacheConfig, redis: Redis) -> CacheGateway:
        return CacheGatewayImpl(config, redis)

from dataclasses import dataclass
from typing import Any

from redis.asyncio import Redis

from prodik.application.interfaces.gateways import CacheGateway
from prodik.infrastructure.config import CacheConfig


@dataclass
class CacheGatewayImpl(CacheGateway):
    config: CacheConfig
    redis: Redis

    async def set(self, key: str, value: Any) -> None:
        await self.redis.set(key, value, self.config.ttl)

    async def get(self, key: str) -> Any:
        return await self.redis.get(key)

import asyncio
import hashlib
from dataclasses import dataclass
from multiprocessing import Process

from dishka import make_async_container

from prodik.application.interfaces.content_processing import RawProcessor
from prodik.application.interfaces.gateways import CacheGateway
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.manage_task.errors import TaskNotFoundError
from prodik.bootstrap.di.providers.connection import ConnectionProvider, RedisProvider
from prodik.domain.task import TaskId
from prodik.infrastructure.config import CacheConfig, Config, PersistenceConfig
from prodik.infrastructure.content_processing.raw.providers import (
    RawHandleProcessProvider,
)
from prodik.infrastructure.content_processing.shared import HandleExecutionContext


class RawHandleProcess(Process):
    def __init__(self, config: Config, *, task_id: TaskId, content: str) -> None:
        self.config = config
        self.task_id = task_id
        self.content = content

        super().__init__()

    def run(self) -> None:
        asyncio.run(self._run_async())

    async def _run_async(self) -> None:
        container = make_async_container(
            RawHandleProcessProvider(),
            ConnectionProvider(),
            RedisProvider(),
            context={
                PersistenceConfig: self.config.persistence,
                CacheConfig: self.config.cache_config,
            },
        )
        cache = await container.get(CacheGateway)
        async with container() as con:
            task_repository = await con.get(TaskRepository)
            predicting_model = await con.get(PredictingModel)
            tx_manager = await con.get(TransactionManager)

            async with tx_manager:
                task = await task_repository.get_by_id(self.task_id)
                if task is None:
                    raise TaskNotFoundError("Task not found")

                with HandleExecutionContext(task):
                    hashed_key = hashlib.sha256(self.content.encode()).hexdigest()
                    result = await cache.get(hashed_key)
                    if result is None:
                        result = predicting_model.process(self.content)
                        await cache.set(hashed_key, result)

                    task.set_result(float(result))
                    await task_repository.update(task)


@dataclass
class RawProcessorImpl(RawProcessor):
    config: Config

    def process(self, task_id: TaskId, content: str) -> None:
        RawHandleProcess(self.config, task_id=task_id, content=content).start()

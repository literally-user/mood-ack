import asyncio
from dataclasses import dataclass
from multiprocessing import Process

from dishka import make_async_container

from prodik.application.errors import TaskNotFoundError
from prodik.application.interfaces.content_processing import RawProcessor
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.bootstrap.di.providers.connection import ConnectionProvider
from prodik.domain.task import TaskId
from prodik.infrastructure.config import Config, PersistenceConfig
from prodik.infrastructure.content_processing.raw.providers import (
    RawHandleProcessProvider,
)
from prodik.infrastructure.content_processing.shared import HandleExecutionContext


class RawHandleProcess(Process):
    config: Config
    task_id: TaskId
    content: str

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
            context={
                PersistenceConfig: self.config.persistence,
            },
        )
        async with container() as con:
            task_repository = await con.get(TaskRepository)
            predicting_model = await con.get(PredictingModel)
            tx_manager = await con.get(TransactionManager)

            async with tx_manager:
                task = await task_repository.get_by_id(self.task_id)
                if task is None:
                    raise TaskNotFoundError("Task not found")

                with HandleExecutionContext(task):
                    result = predicting_model.process(self.content)

                    task.set_result(result)
                    await task_repository.update(task)


@dataclass
class RawProcessorImpl(RawProcessor):
    config: Config

    def process(self, task_id: TaskId, content: str) -> None:
        RawHandleProcess(self.config, task_id=task_id, content=content).start()

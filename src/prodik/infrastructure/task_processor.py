import asyncio
from dataclasses import dataclass
from multiprocessing import Process
from typing import cast

from dishka import Provider, Scope, WithParents, make_async_container, provide_all

from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.task_processor import TaskProcessor
from prodik.bootstrap.di.providers.connection import ConnectionProvider
from prodik.domain.task.model import Task, TaskId
from prodik.infrastructure.config import PersistenceConfig
from prodik.infrastructure.ml.model import PredictingModelImpl
from prodik.infrastructure.repositories import TaskRepositoryImpl
from prodik.infrastructure.transaction_manager import TransactionManagerImpl


class ProcessProvider(Provider):
    provides = provide_all(
        WithParents[TaskRepositoryImpl],
        WithParents[PredictingModelImpl],
        WithParents[TransactionManagerImpl],
        scope=Scope.REQUEST,
    )


class TaskProcess(Process):
    def __init__(
        self, content: str, task_id: TaskId, config: PersistenceConfig
    ) -> None:
        self.config = config
        self.content = content
        self.task_id = task_id

        super().__init__()

    def run(self) -> None:
        asyncio.run(self._run_async())

    async def _run_async(self) -> None:
        container = make_async_container(
            ProcessProvider(),
            ConnectionProvider(),
            context={
                PersistenceConfig: self.config,
            },
        )
        async with container() as container:
            task_repository = await container.get(TaskRepository)
            tx_manager = await container.get(TransactionManagerImpl)
            predicting_model = await container.get(PredictingModel)
            async with tx_manager:
                task = cast("Task", await task_repository.get_by_id(self.task_id))

                result = predicting_model.process(self.content)
                task.set_result(result)

                await task_repository.update(task)


@dataclass
class TaskProcessorImpl(TaskProcessor):
    config: PersistenceConfig

    def process(self, content: str, task: Task) -> None:
        TaskProcess(content, task.id, self.config).start()

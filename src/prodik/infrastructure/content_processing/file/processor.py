import asyncio
from dataclasses import dataclass
from multiprocessing import Process

from dishka import make_async_container

from prodik.application.interfaces.content_processing.file import FileProcessor
from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.manage_task.errors import TaskNotFoundError
from prodik.bootstrap.di.providers.connection import ConnectionProvider, S3Provider
from prodik.domain.task import FileId, TaskId
from prodik.infrastructure.config import Config, ObjectStorageConfig, PersistenceConfig
from prodik.infrastructure.content_processing.file.providers import (
    FileHandleProcessProvider,
)
from prodik.infrastructure.content_processing.file.read import FileReader
from prodik.infrastructure.content_processing.shared import HandleExecutionContext
from prodik.infrastructure.file import FileProcessingRegistry


class FileHandleProcess(Process):
    config: Config
    file_id: FileId
    task_id: TaskId

    def __init__(self, config: Config, *, file_id: FileId, task_id: TaskId) -> None:
        self.config = config
        self.file_id = file_id
        self.task_id = task_id

        super().__init__()

    def run(self) -> None:
        asyncio.run(self._run_async())

    async def _run_async(self) -> None:
        container = make_async_container(
            FileHandleProcessProvider(),
            ConnectionProvider(),
            S3Provider(),
            context={
                PersistenceConfig: self.config.persistence,
                ObjectStorageConfig: self.config.object_storage,
            },
        )
        async with container() as con:
            task_repository = await con.get(TaskRepository)
            predicting_model = await con.get(PredictingModel)
            file_storage_gateway = await con.get(FileStorageGateway)
            file_processing_registry = await con.get(FileProcessingRegistry)
            tx_manager = await con.get(TransactionManager)

            async with tx_manager:
                task = await task_repository.get_by_id(self.task_id)
                if task is None:
                    raise TaskNotFoundError("Task not found")

                with HandleExecutionContext(task):
                    await file_storage_gateway.download_file(self.file_id)

                    file_reader = FileReader(
                        self.config.object_storage, file_processing_registry
                    )
                    content = file_reader.process(self.file_id)

                    result = predicting_model.process(content)

                    task.set_result(result)
                    await task_repository.update(task)


@dataclass
class FileProcessorImpl(FileProcessor):
    config: Config

    def process(self, task_id: TaskId, file_id: FileId) -> None:
        FileHandleProcess(self.config, file_id=file_id, task_id=task_id).start()

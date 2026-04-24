from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import ObjectFileNotFoundError, TaskAlreadyExistsError
from prodik.application.interfaces.content_processing import FileProcessor
from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import (
    FileInputRepository,
    TaskRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import SessionService
from prodik.domain.task import FileId, FileInput, FileInputId, Task, TaskId


@dataclass
class ProcessFileInteractor:
    file_input_repository: FileInputRepository
    file_storage_gateway: FileStorageGateway
    predicting_model: PredictingModel
    session_service: SessionService
    task_repository: TaskRepository
    tx_manager: TransactionManager
    file_processor: FileProcessor

    async def execute(self, file_id: FileId) -> Task:
        async with self.tx_manager:
            auth_meta = await self.session_service.get_authorized_meta()
            if not await self.file_storage_gateway.file_exists(file_id):
                raise ObjectFileNotFoundError("File not found")

            file_input = await self.file_input_repository.get_by_file_id(file_id)
            if file_input is not None:
                raise TaskAlreadyExistsError("Task already exists")

            file_input = FileInput.new(
                id=FileInputId(uuid4()),
                file_id=file_id,
            )

            task = Task.new(
                id=TaskId(uuid4()),
                owner=auth_meta.user,
                input=file_input,
            )
            await self.task_repository.create(task)
            await self.file_input_repository.create(file_input)

            self.file_processor.process(task.id, file_id)

            return task

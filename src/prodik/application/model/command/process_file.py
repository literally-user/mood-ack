from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    ObjectFileNotFoundError,
    UnsupportedFileExtensionError,
)
from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import (
    FileInputRepository,
    TaskRepository,
)
from prodik.application.interfaces.task_processor import TaskProcessor
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import SessionService
from prodik.domain.task import FileId, FileInput, FileInputId, Task, TaskId
from prodik.infrastructure.file import FileProcessingRegistry


@dataclass
class ProcessFileInteractor:
    predicting_model: PredictingModel
    file_storage_gateway: FileStorageGateway
    file_processing_registry: FileProcessingRegistry
    task_repository: TaskRepository
    file_input_repository: FileInputRepository
    task_processor: TaskProcessor
    tx_manager: TransactionManager
    session_service: SessionService

    async def execute(self, file_id: FileId) -> Task:
        async with self.tx_manager:
            auth_meta = await self.session_service.get_authorized_meta()

            file_meta = await self.file_storage_gateway.get_file_info(file_id)
            if file_meta is None:
                raise ObjectFileNotFoundError("File not found")

            file_process_client = self.file_processing_registry.get_client(
                file_meta.extension
            )
            if file_process_client is None:
                raise UnsupportedFileExtensionError("Unsupported file extension")

            readable_content = file_process_client.process(file_meta.content)

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

            self.task_processor.process(readable_content, task)

            return task

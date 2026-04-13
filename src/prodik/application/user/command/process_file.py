from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    ObjectFileNotFoundError,
    UnsupportedFileExtensionError,
)
from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.ml import PredictingModel
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.bootstrap.di.providers.registries import FileProcessingRegistry
from prodik.domain.task import FileId, FileInput, Task, TaskId


@dataclass
class ProcessFileInteractor:
    idp: IdentityProvider
    predicting_model: PredictingModel
    file_storage_gateway: FileStorageGateway
    file_processing_registry: FileProcessingRegistry
    task_repository: TaskRepository
    tx_manager: TransactionManager

    async def execute(self, file_id: FileId) -> Task:
        async with self.tx_manager:
            current_user = await self.idp.get_current_user()

            file_meta = await self.file_storage_gateway.get_file_info(file_id)
            if file_meta is None:
                raise ObjectFileNotFoundError("File not found")

            file_process_client = self.file_processing_registry.get_client(
                file_meta.extension
            )
            if file_process_client is None:
                raise UnsupportedFileExtensionError("Unsupported file extension")

            readable_content = file_process_client.process(file_meta.content)

            task = Task.new(
                id=TaskId(uuid4()), owner=current_user, input=FileInput(file_id)
            )

            self.predicting_model.process(readable_content, task)

            await self.task_repository.create(task)

            return task

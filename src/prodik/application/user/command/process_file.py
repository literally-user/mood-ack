from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    ObjectFileNotFoundError,
    UnsupportedFileExtensionError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.task import FileId, FileInput, FileInputId, Task, TaskId
from prodik.infrastructure.registries import FileProcessingRegistry


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
            current_user_session = await self.idp.get_current_session()
            if current_user_session.is_revoked():
                raise UserSessionRevokedError("Session was revoked")
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

            file_input = FileInput.new(
                id=FileInputId(uuid4()),
                file_id=file_id,
            )
            task = Task.new(
                id=TaskId(uuid4()),
                owner=current_user,
                input=file_input,
            )

            task.set_result(self.predicting_model.process(readable_content, task))

            await self.task_repository.create(task)

            return task

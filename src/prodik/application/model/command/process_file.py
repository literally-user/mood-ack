from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    InvalidCredentialsError,
    ObjectFileNotFoundError,
    UnsupportedFileExtensionError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import (
    FileInputRepository,
    TaskRepository,
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.task_processor import TaskProcessor
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.credentials import IP
from prodik.domain.task import FileId, FileInput, FileInputId, Task, TaskId
from prodik.infrastructure.file import FileProcessingRegistry


@dataclass
class ProcessFileInteractor:
    idp: IdentityProvider
    predicting_model: PredictingModel
    file_storage_gateway: FileStorageGateway
    user_repository: UserRepository
    user_session_repository: UserSessionRepository
    file_processing_registry: FileProcessingRegistry
    task_repository: TaskRepository
    file_input_repository: FileInputRepository
    task_processor: TaskProcessor
    tx_manager: TransactionManager

    async def execute(self, file_id: FileId) -> Task:
        async with self.tx_manager:
            current_user_meta = self.idp.get_user_meta()
            user_ip = self.idp.get_current_ip()

            current_user_session = (
                await self.user_session_repository.get_by_user_id_and_ip(
                    current_user_meta.user_id, IP(user_ip)
                )
            )
            if current_user_session is None:
                raise InvalidCredentialsError("Invalid authorization header format")
            if current_user_session.is_revoked():
                raise UserSessionRevokedError("Session was revoked")

            current_user = await self.user_repository.get_by_uuid(
                current_user_meta.user_id
            )
            if current_user is None:
                raise InvalidCredentialsError("Invalid email or password")

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
            await self.task_repository.create(task)
            await self.file_input_repository.create(file_input)

            self.task_processor.process(readable_content, task)

            return task

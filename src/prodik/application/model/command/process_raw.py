from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import InvalidCredentialsError, UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import (
    RawInputRepository,
    TaskRepository,
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.task_processor import TaskProcessor
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.credentials import IP
from prodik.domain.task import RawInput, RawInputId, Task, TaskId


@dataclass
class ProcessRawInteractor:
    idp: IdentityProvider
    predicting_model: PredictingModel
    tx_manager: TransactionManager
    task_repository: TaskRepository
    raw_input_repository: RawInputRepository
    user_repository: UserRepository
    user_session_repository: UserSessionRepository
    task_processor: TaskProcessor

    async def execute(self, text: str) -> Task:
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

            raw_input = RawInput.new(
                id=RawInputId(uuid4()),
                content=text,
            )
            task = Task.new(
                id=TaskId(uuid4()),
                owner=current_user,
                input=raw_input,
            )
            await self.task_repository.create(task)
            await self.raw_input_repository.create(raw_input)

            self.task_processor.process(text, task)

            return task

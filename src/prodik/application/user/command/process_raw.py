from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.task import RawInput, Task, TaskId


@dataclass
class ProcessRawInteractor:
    idp: IdentityProvider
    predicting_model: PredictingModel
    task_repository: TaskRepository
    tx_manager: TransactionManager

    async def execute(self, text: str) -> Task:
        async with self.tx_manager:
            current_user_session = await self.idp.get_current_session()
            if current_user_session.is_revoked():
                raise UserSessionRevokedError("Session was revoked")
            current_user = await self.idp.get_current_user()

            task = Task.new(
                id=TaskId(uuid4()),
                owner=current_user,
                input=RawInput(text),
            )

            task.set_result(self.predicting_model.process(text, task))

            await self.task_repository.create(task)
            return task

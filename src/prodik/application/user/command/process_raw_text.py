from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.ml import PredictingModel
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.task import RawInput, Task, TaskId


@dataclass
class ProcessRawTextInteractor:
    idp: IdentityProvider
    predicting_model: PredictingModel
    task_repository: TaskRepository
    tx_manager: TransactionManager

    async def execute(self, text: str) -> Task:
        async with self.tx_manager:
            current_user = await self.idp.get_current_user()

            task = Task.new(
                id=TaskId(uuid4()),
                owner=current_user,
                input=RawInput(text),
            )

            self.predicting_model.process(text, task)

            await self.task_repository.create(task)
            return task

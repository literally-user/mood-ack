from dataclasses import dataclass
from uuid import uuid4

from prodik.application.interfaces.predicting_model import PredictingModel
from prodik.application.interfaces.repositories import (
    RawInputRepository,
    TaskRepository,
)
from prodik.application.interfaces.task_processor import TaskProcessor
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import SessionService
from prodik.domain.task import RawInput, RawInputId, Task, TaskId


@dataclass
class ProcessRawInteractor:
    predicting_model: PredictingModel
    tx_manager: TransactionManager
    task_repository: TaskRepository
    raw_input_repository: RawInputRepository
    task_processor: TaskProcessor
    session_service: SessionService

    async def execute(self, text: str) -> Task:
        async with self.tx_manager:
            auth_meta = await self.session_service.get_authorized_meta()

            raw_input = RawInput.new(
                id=RawInputId(uuid4()),
                content=text,
            )
            task = Task.new(
                id=TaskId(uuid4()),
                owner=auth_meta.user,
                input=raw_input,
            )
            await self.task_repository.create(task)
            await self.raw_input_repository.create(raw_input)

            self.task_processor.process(text, task)

            return task

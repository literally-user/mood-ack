from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    TaskRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.manage_task.errors import TaskNotFoundError
from prodik.application.services import SessionService
from prodik.domain.task import TaskId
from prodik.domain.user.services import AccessControlService


@dataclass
class CancelTaskInteractor:
    task_repository: TaskRepository
    access_control_service: AccessControlService
    tx_manager: TransactionManager
    session_service: SessionService

    async def execute(self, task_id: TaskId) -> None:
        async with self.tx_manager:
            auth_meta = await self.session_service.get_authorized_meta()

            task = await self.task_repository.get_by_id(task_id)
            if task is None:
                raise TaskNotFoundError("Task not found")

            self.access_control_service.ensure_can_moderate_task(auth_meta.user, task)

            task.deprecate()
            await self.task_repository.update(task)

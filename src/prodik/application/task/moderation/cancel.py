from dataclasses import dataclass

from prodik.application.errors import (
    NotEnoughRightsError,
    TaskNotFoundError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import TaskRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.task import TaskId


@dataclass
class CancelTaskInteractor:
    idp: IdentityProvider
    task_repository: TaskRepository
    tx_manager: TransactionManager

    async def execute(self, task_id: TaskId) -> None:
        async with self.tx_manager:
            current_user_session = await self.idp.get_current_session()
            if current_user_session.is_revoked():
                raise UserSessionRevokedError("Session was revoked")
            current_user = await self.idp.get_current_user()
            task = await self.task_repository.get_by_id(task_id)
            if task is None:
                raise TaskNotFoundError("Task not found")

            if not current_user.can_manage_tasks() and task.owner_id != current_user.id:
                raise NotEnoughRightsError("Not enough rights to perform operation")

            task.deprecate()
            await self.task_repository.update(task)

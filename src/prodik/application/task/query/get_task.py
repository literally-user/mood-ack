from dataclasses import dataclass

from prodik.application.errors import NotEnoughRightsError, TaskNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import TaskRepository
from prodik.domain.task import Task, TaskId


@dataclass
class GetTaskInteractor:
    idp: IdentityProvider
    task_repository: TaskRepository

    async def execute(self, task_id: TaskId) -> Task:
        current_user = await self.idp.get_current_user()
        task = await self.task_repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        if not current_user.can_manage_tasks() and task.owner_id != current_user.id:
            raise NotEnoughRightsError("Not enough rights to perform operation")

        return task

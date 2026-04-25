from dataclasses import dataclass

from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    TaskRepository,
    UserRepository,
    UserSessionRepository,
)
from prodik.application.manage_task.errors import TaskNotFoundError
from prodik.application.services import SessionService
from prodik.domain.task import Task, TaskId
from prodik.domain.user.services import AccessControlService


@dataclass
class GetTaskInteractor:
    idp: IdentityProvider
    task_repository: TaskRepository
    access_control_service: AccessControlService
    user_session_repository: UserSessionRepository
    user_repository: UserRepository
    session_service: SessionService

    async def execute(self, task_id: TaskId) -> Task:
        auth_meta = await self.session_service.get_authorized_meta()

        task = await self.task_repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        self.access_control_service.ensure_can_get_task(auth_meta.user, task)

        return task

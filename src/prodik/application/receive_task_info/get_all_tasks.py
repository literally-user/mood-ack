from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    TaskRepository,
)
from prodik.application.services import SessionService
from prodik.domain.task import Task
from prodik.domain.user.services import AccessControlService


@dataclass
class GetAllTasksInteractor:
    access_control_service: AccessControlService
    task_repository: TaskRepository
    session_service: SessionService

    async def execute(self, page: int, size: int) -> list[Task]:
        auth_meta = await self.session_service.get_authorized_meta()

        self.access_control_service.ensure_can_get_all_tasks(auth_meta.user)

        return await self.task_repository.get_all(page, size)

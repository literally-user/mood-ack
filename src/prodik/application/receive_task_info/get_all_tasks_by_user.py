from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    TaskRepository,
)
from prodik.application.services import SessionService
from prodik.domain.task import Task


@dataclass
class GetAllTasksByUserInteractor:
    task_repository: TaskRepository
    session_service: SessionService

    async def execute(self, page: int, size: int) -> list[Task]:
        auth_meta = await self.session_service.get_authorized_meta()

        return await self.task_repository.get_all_by_user_id(
            auth_meta.user.id, page, size
        )

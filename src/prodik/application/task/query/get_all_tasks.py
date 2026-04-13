from dataclasses import dataclass

from prodik.application.errors import NotEnoughRightsError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import TaskRepository
from prodik.domain.task import Task


@dataclass
class GetAllTasksInteractor:
    idp: IdentityProvider
    task_repository: TaskRepository

    async def execute(self, page: int, size: int) -> list[Task]:
        current_user = await self.idp.get_current_user()
        if not current_user.can_manage_tasks():
            raise NotEnoughRightsError("Not enough rights to perform operation")

        return await self.task_repository.get_all(page, size)

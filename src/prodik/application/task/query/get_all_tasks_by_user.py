from dataclasses import dataclass

from prodik.application.errors import UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import TaskRepository
from prodik.domain.task import Task


@dataclass
class GetAllTasksByUserInteractor:
    idp: IdentityProvider
    task_repository: TaskRepository

    async def execute(self, page: int, size: int) -> list[Task]:
        current_user_session = await self.idp.get_current_session()
        if current_user_session.is_revoked():
            raise UserSessionRevokedError("Session was revoked")
        current_user = await self.idp.get_current_user()

        return await self.task_repository.get_all_by_user_id(
            current_user.id, page, size
        )

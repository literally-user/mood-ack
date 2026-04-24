from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    UserRepository,
)
from prodik.application.services import SessionService
from prodik.domain.user import User
from prodik.domain.user.services import AccessControlService


@dataclass
class GetAllUsersInteractor:
    session_service: SessionService
    access_control_service: AccessControlService
    user_repository: UserRepository

    async def execute(self, page: int, size: int) -> list[User]:
        auth_meta = await self.session_service.get_authorized_meta()

        self.access_control_service.ensure_can_get_all_users(auth_meta.user)

        return await self.user_repository.get_all(page, size)

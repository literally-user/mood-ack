from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    UserRepository,
)
from prodik.application.manage_user.errors import UserNotFoundError
from prodik.application.services import SessionService
from prodik.domain.user import User, UserId


@dataclass
class GetUserProfileInteractor:
    session_service: SessionService
    user_repository: UserRepository

    async def execute(self, target_id: UserId) -> User:
        await self.session_service.get_authorized_meta()

        user = await self.user_repository.get_by_uuid(target_id)
        if user is None:
            raise UserNotFoundError("User not found")

        return user

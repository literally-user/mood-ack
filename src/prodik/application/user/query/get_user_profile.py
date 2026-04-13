from dataclasses import dataclass

from prodik.application.errors import UserNotFoundError
from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import User, UserId


@dataclass
class GetUserProfileInteractor:
    user_repository: UserRepository

    async def execute(self, target_id: UserId) -> User:
        user = await self.user_repository.get_by_uuid(target_id)
        if user is None:
            raise UserNotFoundError("User not found")

        return user

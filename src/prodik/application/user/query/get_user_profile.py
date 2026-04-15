from dataclasses import dataclass

from prodik.application.errors import UserNotFoundError, UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import User, UserId


@dataclass
class GetUserProfileInteractor:
    user_repository: UserRepository
    idp: IdentityProvider

    async def execute(self, target_id: UserId) -> User:
        current_user_session = await self.idp.get_current_session()
        if current_user_session.is_revoked():
            raise UserSessionRevokedError("Session was revoked")
        user = await self.user_repository.get_by_uuid(target_id)
        if user is None:
            raise UserNotFoundError("User not found")

        return user

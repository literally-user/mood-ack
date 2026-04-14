from dataclasses import dataclass

from prodik.application.errors import NotEnoughRightsError, UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import User


@dataclass
class GetAllUsersInteractor:
    user_repository: UserRepository
    idp: IdentityProvider

    async def execute(self, page: int, size: int) -> list[User]:
        current_user = await self.idp.get_current_user()
        current_user_session = await self.idp.get_current_session()
        if current_user_session.is_revoked():
            UserSessionRevokedError("Session was revoked")
        if not current_user.can_manage_users():
            raise NotEnoughRightsError("Not enough rights to perform operation")

        return await self.user_repository.get_all(page, size)

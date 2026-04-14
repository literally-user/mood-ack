from dataclasses import dataclass

from prodik.application.errors import UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.domain.user import User


@dataclass
class GetCurrentProfileInteractor:
    idp: IdentityProvider

    async def execute(self) -> User:
        current_user_session = await self.idp.get_current_session()
        if current_user_session.is_revoked():
            UserSessionRevokedError("Session was revoked")
        return await self.idp.get_current_user()

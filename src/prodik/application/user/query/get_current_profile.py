from dataclasses import dataclass

from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.domain.user import User


@dataclass
class GetCurrentProfileInteractor:
    idp: IdentityProvider

    async def execute(self) -> User:
        return await self.idp.get_current_user()

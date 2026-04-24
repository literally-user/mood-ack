from dataclasses import dataclass

from prodik.application.services.session_service import SessionService
from prodik.domain.user import User


@dataclass
class GetCurrentProfileInteractor:
    session_service: SessionService

    async def execute(self) -> User:
        return (await self.session_service.get_authorized_meta()).user

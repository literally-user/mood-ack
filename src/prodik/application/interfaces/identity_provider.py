from typing import Protocol

from prodik.domain.credentials import UserSession
from prodik.domain.user import User


class IdentityProvider(Protocol):
    async def get_current_user(self) -> User: ...
    async def get_current_session(self) -> UserSession: ...
    def get_current_ip(self) -> str: ...

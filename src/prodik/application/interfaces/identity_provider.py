from typing import Protocol

from prodik.domain.user import User


class IdentityProvider(Protocol):
    async def get_current_user(self) -> User: ...

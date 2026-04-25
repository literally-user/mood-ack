from typing import Protocol

from prodik.domain.credentials import OAuthAuthorization
from prodik.domain.user import UserId


class OAuthAuthorizationRepository(Protocol):
    async def get_by_user_id(self, user_id: UserId) -> OAuthAuthorization | None: ...

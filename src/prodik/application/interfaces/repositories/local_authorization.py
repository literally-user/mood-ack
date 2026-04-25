from typing import Protocol

from prodik.domain.credentials import LocalAuthorization
from prodik.domain.user import UserId


class LocalAuthorizationRepository(Protocol):
    async def create(self, local_authorization: LocalAuthorization) -> None: ...
    async def update(self, local_authorization: LocalAuthorization) -> None: ...
    async def get_by_user_id(self, id: UserId) -> LocalAuthorization | None: ...

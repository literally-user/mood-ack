from typing import Protocol, TypedDict
from uuid import UUID

from prodik.domain.user import UserRole


class UserData(TypedDict):
    uuid: UUID
    role: UserRole


class TokenManager(Protocol):
    def encode(self, user_id: UUID, user_role: UserRole) -> str: ...
    def decode(self, token: str) -> UserData: ...

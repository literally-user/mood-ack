from typing import Protocol, TypedDict
from uuid import UUID

from prodik.domain.user import User, UserRole


class UserData(TypedDict):
    uuid: UUID
    role: UserRole


class TokenManager(Protocol):
    def generate_access_token(self, user: User, expires_in: int) -> str: ...
    def decode_access_token(self, token: str) -> UserData: ...
    def generate_refresh_token(self) -> str: ...

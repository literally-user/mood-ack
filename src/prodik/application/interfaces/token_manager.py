from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from prodik.domain.user import User, UserRole


@dataclass(slots=True, frozen=True, kw_only=True)
class UserData:
    uuid: UUID
    role: UserRole


@dataclass(slots=True, frozen=True, kw_only=True)
class StateData:
    provider: str


@dataclass(slots=True, frozen=True, kw_only=True)
class OAuthData:
    email: str


class AccessTokenManager(Protocol):
    def generate(self, user: User, expires_in: int) -> str: ...
    def decode(self, token: str) -> UserData: ...


class RefreshTokenManager(Protocol):
    def generate(self) -> str: ...


class StateTokenManager(Protocol):
    def generate(self, data: StateData) -> str: ...
    def decode(self, token: str) -> StateData: ...


class OAuthTokenManager(Protocol):
    def decode(self, token: str) -> OAuthData: ...

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from prodik.application.interfaces.token_manager import (
    AccessTokenManager,
    OAuthData,
    OAuthTokenManager,
    RefreshTokenManager,
    StateData,
    StateTokenManager,
    UserData,
)
from prodik.domain.user import User, UserRole
from prodik.infrastructure.config import Config


@dataclass
class AccessTokenManagerImpl(AccessTokenManager):
    _config: Config

    def generate(self, user: User, expires_in: int) -> str:
        now = datetime.now(tz=UTC)

        payload = {
            "sub": str(user.id),
            "role": user.role.value,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
        }

        return jwt.encode(
            payload,
            self._config.api.secret,
            algorithm="HS256",
        )

    def decode(self, token: str) -> UserData:
        data = jwt.decode(
            token,
            self._config.api.secret,
            algorithms=["HS256"],
        )

        return UserData(
            uuid=UUID(data["sub"]),
            role=UserRole(data["role"]),
            expires_in=data["exp"],
        )


@dataclass
class RefreshTokenManagerImpl(RefreshTokenManager):
    def generate(self) -> str:
        return secrets.token_urlsafe(64)


@dataclass
class StateTokenManagerImpl(StateTokenManager):
    _config: Config

    def generate(self, data: StateData) -> str:
        now = datetime.now(tz=UTC)

        payload = {
            "provider": data.provider,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
        }

        return jwt.encode(
            payload,
            self._config.api.secret,
            algorithm="HS256",
        )

    def decode(self, token: str) -> StateData:
        data = jwt.decode(
            token,
            self._config.api.secret,
            algorithms=["HS256"],
        )

        return StateData(
            provider=data["provider"],
        )


@dataclass
class OAuthTokenManagerImpl(OAuthTokenManager):
    def decode(self, token: str) -> OAuthData:
        data = jwt.decode(token, options={"verify_signature": False})

        return OAuthData(
            email=data["email"],
        )

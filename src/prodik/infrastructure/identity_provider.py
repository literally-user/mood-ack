from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

from fastapi import Request

from prodik.application.errors import AccessTokenExpiredError, InvalidCredentialsError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.token_manager import AccessTokenManager, UserData
from prodik.domain.credentials import IP, UserSession
from prodik.domain.user import User

TOKEN_HEADER_PARTS: Final[int] = 2
TOKEN_TYPE = "Bearer"  # noqa: S105


@dataclass
class IdentityProviderImpl(IdentityProvider):
    _user_session_repository: UserSessionRepository
    _access_token_manager: AccessTokenManager
    _user_repository: UserRepository
    _request: Request

    def _get_token_data(self) -> UserData:
        header = self._request.headers.get("Authorization")
        if header is None:
            raise InvalidCredentialsError("Authorization header not found")

        parts = header.split(" ")
        if len(parts) != TOKEN_HEADER_PARTS:
            raise InvalidCredentialsError("Invalid authorization header format")

        token_type, token = parts
        if token_type != TOKEN_TYPE:
            raise InvalidCredentialsError("Invalid authorization header format")

        data = self._access_token_manager.decode(token)
        if data.expires_in >= datetime.now(tz=UTC).timestamp():
            raise AccessTokenExpiredError("Access token expired")

        return data

    def _get_client_ip(self) -> IP:
        client = self._request.client
        if client is None:
            raise RuntimeError("Cannot determine client IP")
        return IP(client.host)

    async def get_current_user(self) -> User:
        data = self._get_token_data()
        user = await self._user_repository.get_by_uuid(data.uuid)
        if user is None:
            raise InvalidCredentialsError("Invalid authorization header format")

        return user

    async def get_current_session(self) -> UserSession:
        data = self._get_token_data()
        user = await self._user_repository.get_by_uuid(data.uuid)
        if user is None:
            raise InvalidCredentialsError("Invalid authorization header format")

        session = await self._user_session_repository.get_by_user_id_and_ip(
            user.id, self._get_client_ip()
        )
        if session is None:
            raise InvalidCredentialsError("Invalid authorization header format")

        return session

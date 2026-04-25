from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

from fastapi import Request

from prodik.application.authorization.errors import (
    AccessTokenExpiredError,
    InvalidCredentialsError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.token_manager import AccessTokenManager, UserData

TOKEN_HEADER_PARTS: Final[int] = 2
TOKEN_TYPE = "Bearer"  # noqa: S105


@dataclass
class IdentityProviderImpl(IdentityProvider):
    _access_token_manager: AccessTokenManager
    _request: Request

    def get_user_meta(self) -> UserData:
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
        if data.expires_in <= datetime.now(tz=UTC).timestamp():
            raise AccessTokenExpiredError("Access token expired")

        return data

    def get_current_ip(self) -> str:
        if self._request.client is None:
            raise InvalidCredentialsError("Failed to determine client IP")

        return self._request.client.host

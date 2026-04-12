from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import InvalidCredentialsError, UserDeactivatedError
from prodik.application.interfaces.repositories import (
    OAuthAuthorizationRepository,
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.sso import OAuthClientRegistry
from prodik.application.interfaces.token_manager import (
    AccessTokenManager,
    OAuthTokenManager,
    RefreshTokenManager,
    StateTokenManager,
)
from prodik.domain.credentials import IP, UserSession, UserSessionId
from prodik.domain.user import Email
from prodik.infrastructure.config import Config


@dataclass(slots=True, frozen=True, kw_only=True)
class OAuthLoginResponseDTO:
    refresh_token: str
    access_token: str

    expires_in: int


@dataclass
class OAuthLoginInteractor:
    _authorization_repository: OAuthAuthorizationRepository
    _user_session_repository: UserSessionRepository
    _state_token_manager: StateTokenManager
    _oauth_token_manager: OAuthTokenManager
    _client_registry: OAuthClientRegistry
    _refresh_token_manager: RefreshTokenManager
    _access_token_manager: AccessTokenManager
    _user_repository: UserRepository
    _config: Config

    async def execute(
        self, authorization_code: str, state_token: str, ip: str
    ) -> OAuthLoginResponseDTO:
        provider = self._state_token_manager.decode(state_token).provider
        client = self._client_registry.get_client(provider)

        client_data = await client.exchange_code(authorization_code)
        oauth_data = self._oauth_token_manager.decode(client_data.token_id)

        user = await self._user_repository.get_by_email(Email(oauth_data.email))
        if user is None:
            raise InvalidCredentialsError("Invalid email or password")

        if user.deactivated():
            raise UserDeactivatedError("User deactivated")

        refresh_token = self._refresh_token_manager.generate()
        access_token = self._access_token_manager.generate(
            user, expires_in=self._config.api.expires_in
        )
        user_session = await self._user_session_repository.get_by_user_id_and_ip(
            user.id, IP(ip)
        )
        if user_session is None:
            await self._user_session_repository.create(
                UserSession.new(
                    id=UserSessionId(uuid4()),
                    user=user,
                    ip=ip,
                    refresh_token=refresh_token,
                )
            )
        elif user_session.is_revoked():
            user_session.enable()
            user_session.update_refresh_token(refresh_token)

        return OAuthLoginResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._config.api.expires_in,
        )

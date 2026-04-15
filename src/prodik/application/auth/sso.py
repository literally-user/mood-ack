from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    InvalidCredentialsError,
    UnsupportedProviderError,
    UserDeactivatedError,
)
from prodik.application.interfaces.repositories import (
    OAuthAuthorizationRepository,
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.token_manager import (
    AccessTokenManager,
    OAuthTokenManager,
    RefreshTokenManager,
    StateTokenManager,
)
from prodik.domain.credentials import IP, UserSession, UserSessionId
from prodik.domain.user import Email
from prodik.infrastructure.config import APIConfig
from prodik.infrastructure.registries import OAuthClientRegistry


@dataclass(slots=True, frozen=True, kw_only=True)
class OAuthLoginResponseDTO:
    refresh_token: str
    access_token: str

    expires_in: int


@dataclass
class OAuthLoginInteractor:
    authorization_repository: OAuthAuthorizationRepository
    user_session_repository: UserSessionRepository
    state_token_manager: StateTokenManager
    oauth_token_manager: OAuthTokenManager
    client_registry: OAuthClientRegistry
    refresh_token_manager: RefreshTokenManager
    access_token_manager: AccessTokenManager
    user_repository: UserRepository
    config: APIConfig

    async def execute(
        self, authorization_code: str, state_token: str, ip: str
    ) -> OAuthLoginResponseDTO:
        provider = self.state_token_manager.decode(state_token).provider
        client = self.client_registry.get_client(provider)
        if client is None:
            raise UnsupportedProviderError("Unsupported OAuth provider")

        client_data = await client.exchange_code(authorization_code)
        oauth_data = self.oauth_token_manager.decode(client_data.token_id)

        user = await self.user_repository.get_by_email(Email(oauth_data.email))
        if user is None:
            raise InvalidCredentialsError("Invalid email or password")

        if user.is_deactivated():
            raise UserDeactivatedError("User deactivated")

        refresh_token = self.refresh_token_manager.generate()
        access_token = self.access_token_manager.generate(
            user, expires_in=self.config.expires_in
        )
        user_session = await self.user_session_repository.get_by_user_id_and_ip(
            user.id, IP(ip)
        )
        if user_session is None:
            await self.user_session_repository.create(
                UserSession.new(
                    id=UserSessionId(uuid4()),
                    user=user,
                    ip=ip,
                    refresh_token=refresh_token,
                )
            )
        else:
            if user_session.is_revoked():
                user_session.enable()
            user_session.update_refresh_token(refresh_token)
            await self.user_session_repository.update(user_session)

        return OAuthLoginResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.config.expires_in,
        )

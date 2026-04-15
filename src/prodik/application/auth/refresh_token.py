from dataclasses import dataclass

from prodik.application.errors import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.repositories import (
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.token_manager import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.infrastructure.config import APIConfig


@dataclass(slots=True, frozen=True, kw_only=True)
class RefreshTokenResponseDTO:
    access_token: str
    refresh_token: str

    expires_in: int


@dataclass
class RefreshTokenInteractor:
    user_session_repository: UserSessionRepository
    transaction_manager: TransactionManager
    access_token_manager: AccessTokenManager
    user_repository: UserRepository
    refresh_token_manager: RefreshTokenManager
    config: APIConfig

    async def execute(self, token: str) -> RefreshTokenResponseDTO:
        async with self.transaction_manager:
            user_session = await self.user_session_repository.get_by_token(token)
            if user_session is None:
                raise InvalidCredentialsError("Invalid token format")

            if user_session.is_revoked():
                raise UserSessionRevokedError("Session was revoked")

            user = await self.user_repository.get_by_uuid(user_session.user_id)
            if user is None:
                raise UserNotFoundError("User not found")

            access_token = self.access_token_manager.generate(
                user, self.config.expires_in
            )
            refresh_token = self.refresh_token_manager.generate()

            user_session.update_refresh_token(refresh_token)
            await self.user_session_repository.update(user_session)

            return RefreshTokenResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.config.expires_in,
            )

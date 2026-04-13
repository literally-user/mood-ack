from dataclasses import dataclass

from prodik.application.errors import InvalidCredentialsError, UserDeactivatedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    LocalAuthorizationRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.token_manager import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.credentials import IP
from prodik.infrastructure.config import Config


@dataclass(slots=True, frozen=True, kw_only=True)
class ChangePasswordRequestDTO:
    old_password: str
    new_password: str

    ip: IP


@dataclass(slots=True, frozen=True, kw_only=True)
class ChangePasswordResponseDTO:
    access_token: str
    refresh_token: str

    expires_in: int


@dataclass
class ChangePasswordInteractor:
    local_authorization_repository: LocalAuthorizationRepository
    user_session_repository: UserSessionRepository
    password_hasher: PasswordHasher
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    tx_manager: TransactionManager
    config: Config
    idp: IdentityProvider

    async def execute(
        self, request: ChangePasswordRequestDTO
    ) -> ChangePasswordResponseDTO:
        async with self.tx_manager:
            current_user_session = await self.idp.get_current_session()
            current_user = await self.idp.get_current_user()
            if current_user.is_deactivated():
                raise UserDeactivatedError("User deactivated")

            current_user_sessions = (
                await self.user_session_repository.get_all_by_user_id(current_user.id)
            )
            local_authorization = (
                await self.local_authorization_repository.get_by_user_id(
                    current_user.id
                )
            )

            if not self.password_hasher.verify(
                local_authorization.password, request.old_password
            ):
                raise InvalidCredentialsError("Wrong old password")

            for session in current_user_sessions:
                if session != current_user_session:
                    session.revoke()

            hashed_password = self.password_hasher.hash(request.new_password)
            local_authorization.change_password(hashed_password)

            refresh_token = self.refresh_token_manager.generate()
            access_token = self.access_token_manager.generate(
                current_user, self.config.api.expires_in
            )

            await self.local_authorization_repository.update(local_authorization)
            await self.user_session_repository.update_many(
                [*current_user_sessions, current_user_session]
            )

            return ChangePasswordResponseDTO(
                refresh_token=refresh_token,
                access_token=access_token,
                expires_in=self.config.api.expires_in,
            )

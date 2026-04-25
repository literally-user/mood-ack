from dataclasses import dataclass

from prodik.application.auth.errors import (
    InvalidCredentialsError,
)
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    LocalAuthorizationRepository,
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.token_manager import (
    AccessTokenManager,
    RefreshTokenManager,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import SessionService
from prodik.infrastructure.config import APIConfig


@dataclass(slots=True, frozen=True, kw_only=True)
class ChangePasswordRequestDTO:
    old_password: str
    new_password: str


@dataclass(slots=True, frozen=True, kw_only=True)
class ChangePasswordResponseDTO:
    access_token: str
    refresh_token: str

    expires_in: int


@dataclass
class ChangePasswordInteractor:
    session_service: SessionService
    local_authorization_repository: LocalAuthorizationRepository
    user_session_repository: UserSessionRepository
    user_repository: UserRepository
    password_hasher: PasswordHasher
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    tx_manager: TransactionManager
    config: APIConfig

    async def execute(
        self, request: ChangePasswordRequestDTO
    ) -> ChangePasswordResponseDTO:
        async with self.tx_manager:
            auth_meta = await self.session_service.get_authorized_meta()

            current_user_sessions = (
                await self.user_session_repository.get_all_by_user_id(auth_meta.user.id)
            )
            local_authorization = (
                await self.local_authorization_repository.get_by_user_id(
                    auth_meta.user.id
                )
            )
            if local_authorization is None:
                raise InvalidCredentialsError("Invalid email or password")
            if not self.password_hasher.verify(
                local_authorization.password, request.old_password
            ):
                raise InvalidCredentialsError("Wrong old password")

            for session in current_user_sessions:
                if session != auth_meta.session:
                    session.revoke()

            hashed_password = self.password_hasher.hash(request.new_password)
            local_authorization.change_password(hashed_password)

            refresh_token = self.refresh_token_manager.generate()
            access_token = self.access_token_manager.generate(
                auth_meta.user,
                self.config.expires_in,
            )
            auth_meta.session.update_refresh_token(refresh_token)

            await self.local_authorization_repository.update(local_authorization)
            await self.user_session_repository.update_many(
                [*current_user_sessions, auth_meta.session]
            )

            return ChangePasswordResponseDTO(
                refresh_token=refresh_token,
                access_token=access_token,
                expires_in=self.config.expires_in,
            )

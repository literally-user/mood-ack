from dataclasses import dataclass

from prodik.application.errors import InvalidCredentialsError, UserDeactivatedError
from prodik.application.interfaces.identity_provider import IdentityProvider
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
    _local_authorization_repository: LocalAuthorizationRepository
    _user_session_repository: UserSessionRepository
    _user_repository: UserRepository
    _password_hasher: PasswordHasher
    _access_token_manager: AccessTokenManager
    _refresh_token_manager: RefreshTokenManager
    _tx_manager: TransactionManager
    _config: Config
    _idp: IdentityProvider

    async def execute(
        self, request: ChangePasswordRequestDTO
    ) -> ChangePasswordResponseDTO:
        async with self._tx_manager:
            current_user = await self._idp.get_current_user()
            if current_user.deactivated():
                raise UserDeactivatedError("User deactivated")

            current_user_sessions = (
                await self._user_session_repository.get_all_by_user_id(current_user.id)
            )
            local_authorization = (
                await self._local_authorization_repository.get_by_user_id(
                    current_user.id
                )
            )

            if not self._password_hasher.verify(
                local_authorization.password, request.old_password
            ):
                raise InvalidCredentialsError("Wrong old password")

            access_token = self._access_token_manager.generate(
                current_user, expires_in=self._config.api.expires_in
            )
            hashed_password = self._password_hasher.hash(request.new_password)

            current_user_session = next(
                session for session in current_user_sessions if session.ip == request.ip
            )
            for session in current_user_sessions:
                refresh_token = self._refresh_token_manager.generate()
                session.update_refresh_token(refresh_token)

            local_authorization.change_password(hashed_password)

            await self._local_authorization_repository.update(local_authorization)
            await self._user_session_repository.update_many(current_user_sessions)

            return ChangePasswordResponseDTO(
                access_token=access_token,
                refresh_token=current_user_session.ip,
                expires_in=self._config.api.expires_in,
            )

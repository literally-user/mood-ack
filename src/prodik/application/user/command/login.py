from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    InvalidCredentialsError,
    UserDeactivatedError,
    UserNotFoundError,
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
from prodik.domain.credentials import IP, UserSession, UserSessionId
from prodik.domain.user import Email
from prodik.infrastructure.config import Config


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginRequestDTO:
    password: str
    email: str
    ip: str


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginResponseDTO:
    refresh_token: str
    access_token: str

    expires_in: int


@dataclass
class LoginInteractor:
    _tx_manager: TransactionManager
    _password_hasher: PasswordHasher
    _access_token_manager: AccessTokenManager
    _refresh_token_manager: RefreshTokenManager
    _user_repository: UserRepository
    _local_authorization_repository: LocalAuthorizationRepository
    _user_session_repository: UserSessionRepository
    _config: Config

    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        async with self._tx_manager:
            user = await self._user_repository.get_by_email(Email(request.email))
            if user is None:
                raise UserNotFoundError("Invalid email or password")

            if user.deactivated():
                raise UserDeactivatedError("User deactivated")

            authorization = await self._local_authorization_repository.get_by_user_id(
                user.id
            )

            if not self._password_hasher.verify(
                authorization.password, request.password
            ):
                raise InvalidCredentialsError("Invalid email or password")

            refresh_token = self._refresh_token_manager.generate()
            access_token = self._access_token_manager.generate(
                user, expires_in=self._config.api.expires_in
            )
            user_session = await self._user_session_repository.get_by_user_id_and_ip(
                user.id, IP(request.ip)
            )
            if user_session is None:
                await self._user_session_repository.create(
                    UserSession.new(
                        id=UserSessionId(uuid4()),
                        user=user,
                        ip=request.ip,
                        refresh_token=refresh_token,
                    )
                )
            else:
                if user_session.is_revoked():
                    user_session.enable()
                    user_session.update_refresh_token(refresh_token)

                await self._user_session_repository.update(user_session)

            return LoginResponseDTO(
                refresh_token=refresh_token,
                access_token=access_token,
                expires_in=self._config.api.expires_in,
            )

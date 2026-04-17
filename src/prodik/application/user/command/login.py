from dataclasses import dataclass
from uuid import uuid4

from prodik.application.errors import (
    InvalidCredentialsError,
    LocalAuthorizationNotFoundError,
    UserDeactivatedError,
    UserNotFoundError,
)
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
from prodik.domain.credentials import IP, UserSession, UserSessionId
from prodik.domain.user import Email
from prodik.infrastructure.config import APIConfig


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginRequestDTO:
    password: str
    email: str


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginResponseDTO:
    refresh_token: str
    access_token: str

    expires_in: int


@dataclass
class LoginInteractor:
    tx_manager: TransactionManager
    password_hasher: PasswordHasher
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    user_repository: UserRepository
    local_authorization_repository: LocalAuthorizationRepository
    user_session_repository: UserSessionRepository
    idp: IdentityProvider
    config: APIConfig

    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        async with self.tx_manager:
            user_ip = self.idp.get_current_ip()
            user = await self.user_repository.get_by_email(Email(request.email))
            if user is None:
                raise UserNotFoundError("Invalid email or password")

            if user.is_deactivated():
                raise UserDeactivatedError("User deactivated")

            authorization = await self.local_authorization_repository.get_by_user_id(
                user.id
            )
            if authorization is None:
                raise LocalAuthorizationNotFoundError("Local authorization not found")

            if not self.password_hasher.verify(
                authorization.password, request.password
            ):
                raise InvalidCredentialsError("Invalid email or password")

            refresh_token = self.refresh_token_manager.generate()
            access_token = self.access_token_manager.generate(
                user, expires_in=self.config.expires_in
            )
            user_session = await self.user_session_repository.get_by_user_id_and_ip(
                user.id, IP(user_ip)
            )
            if user_session is None:
                await self.user_session_repository.create(
                    UserSession.new(
                        id=UserSessionId(uuid4()),
                        user=user,
                        ip=user_ip,
                        refresh_token=refresh_token,
                    )
                )
            else:
                if user_session.is_revoked():
                    user_session.enable()
                user_session.update_refresh_token(refresh_token)

                await self.user_session_repository.update(user_session)

            return LoginResponseDTO(
                refresh_token=refresh_token,
                access_token=access_token,
                expires_in=self.config.expires_in,
            )

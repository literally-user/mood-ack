from dataclasses import dataclass
from uuid import uuid4

from prodik.application.authorization.errors import UserAlreadyExistsError
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
from prodik.domain.credentials import (
    LocalAuthorization,
    LocalAuthorizationId,
    UserSession,
    UserSessionId,
)
from prodik.domain.user import Email, User, UserId
from prodik.infrastructure.config import APIConfig


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterRequestDTO:
    username: str
    first_name: str
    last_name: str
    email: str
    password: str
    age: int


@dataclass(slots=True, frozen=True, kw_only=True)
class RegisterResponseDTO:
    refresh_token: str
    access_token: str

    expires_in: int


@dataclass
class RegisterInteractor:
    local_authorization_repository: LocalAuthorizationRepository
    user_session_repository: UserSessionRepository
    access_token_manager: AccessTokenManager
    refresh_token_manager: RefreshTokenManager
    password_hasher: PasswordHasher
    user_repository: UserRepository
    tx_manager: TransactionManager
    idp: IdentityProvider
    config: APIConfig

    async def execute(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        async with self.tx_manager:
            user_ip = self.idp.get_current_ip()
            user = await self.user_repository.get_by_email(Email(request.email))
            if user is not None:
                raise UserAlreadyExistsError("User already exists")

            user_id = UserId(uuid4())
            user = User.new(
                id=user_id,
                username=request.username,
                first_name=request.first_name,
                last_name=request.last_name,
                email=request.email,
                age=request.age,
            )

            refresh_token = self.refresh_token_manager.generate()
            access_token = self.access_token_manager.generate(
                user,
                expires_in=self.config.expires_in,
            )
            local_authorization = LocalAuthorization.new(
                id=LocalAuthorizationId(uuid4()),
                user=user,
                password=self.password_hasher.hash(request.password),
            )

            user_session = UserSession.new(
                id=UserSessionId(uuid4()),
                user=user,
                ip=user_ip,
                refresh_token=refresh_token,
            )
            await self.user_repository.create(user)
            await self.local_authorization_repository.create(local_authorization)
            await self.user_session_repository.create(user_session)

            return RegisterResponseDTO(
                refresh_token=refresh_token,
                access_token=access_token,
                expires_in=self.config.expires_in,
            )

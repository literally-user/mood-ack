from dataclasses import dataclass

from prodik.application.errors import InvalidCredentialsError, UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.credentials import IP


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateCurrentProfileRequestDTO:
    email: str | None
    first_name: str | None
    last_name: str | None
    age: int | None
    username: str | None


@dataclass
class UpdateCurrentProfileInteractor:
    user_session_repository: UserSessionRepository
    user_repository: UserRepository
    tx_manager: TransactionManager
    idp: IdentityProvider

    async def execute(self, request: UpdateCurrentProfileRequestDTO) -> None:
        async with self.tx_manager:
            current_user_meta = self.idp.get_user_meta()
            user_ip = self.idp.get_current_ip()

            current_user_session = (
                await self.user_session_repository.get_by_user_id_and_ip(
                    current_user_meta.user_id, IP(user_ip)
                )
            )
            if current_user_session is None:
                raise InvalidCredentialsError("Invalid authorization header format")
            if current_user_session.is_revoked():
                raise UserSessionRevokedError("Session was revoked")

            current_user = await self.user_repository.get_by_uuid(
                current_user_meta.user_id
            )
            if current_user is None:
                raise InvalidCredentialsError("Invalid email or password")

            if request.age is not None:
                current_user.change_age(request.age)
            if request.first_name is not None:
                current_user.change_first_name(request.first_name)
            if request.last_name is not None:
                current_user.change_last_name(request.last_name)
            if request.email is not None:
                current_user.change_email(request.email)
            if request.username is not None:
                current_user.change_username(request.username)

            await self.user_repository.update(current_user)

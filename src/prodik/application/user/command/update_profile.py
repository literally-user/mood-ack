from dataclasses import dataclass

from prodik.application.errors import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.credentials import IP
from prodik.domain.user import UserId
from prodik.domain.user.services import AccessControlService


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateProfileRequestDTO:
    email: str | None
    first_name: str | None
    last_name: str | None
    age: int | None
    username: str | None


@dataclass
class UpdateProfileInteractor:
    access_control_service: AccessControlService
    user_session_repository: UserSessionRepository
    user_repository: UserRepository
    tx_manager: TransactionManager
    idp: IdentityProvider

    async def execute(
        self, request: UpdateProfileRequestDTO, target_id: UserId
    ) -> None:
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

            if current_user.id == target_id:
                target_user = current_user
            else:
                target_user = await self.user_repository.get_by_uuid(target_id)  # type: ignore
                if target_user is None:
                    raise UserNotFoundError("User not found")

            self.access_control_service.ensure_can_update_profile(
                current_user, target_user
            )

            target_user.update_profile(
                request.age,
                request.first_name,
                request.last_name,
                request.email,
                request.username,
            )

            await self.user_repository.update(target_user)

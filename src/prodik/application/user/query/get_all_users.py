from dataclasses import dataclass

from prodik.application.errors import (
    InvalidCredentialsError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    UserRepository,
    UserSessionRepository,
)
from prodik.domain.credentials import IP
from prodik.domain.user import User
from prodik.domain.user.services import AccessControlService


@dataclass
class GetAllUsersInteractor:
    access_control_service: AccessControlService
    user_session_repository: UserSessionRepository
    user_repository: UserRepository
    idp: IdentityProvider

    async def execute(self, page: int, size: int) -> list[User]:
        current_user_meta = self.idp.get_user_meta()
        user_ip = self.idp.get_current_ip()

        current_user_session = await self.user_session_repository.get_by_user_id_and_ip(
            current_user_meta.user_id, IP(user_ip)
        )
        if current_user_session is None:
            raise InvalidCredentialsError("Invalid authorization header format")
        if current_user_session.is_revoked():
            raise UserSessionRevokedError("Session was revoked")

        current_user = await self.user_repository.get_by_uuid(current_user_meta.user_id)
        if current_user is None:
            raise InvalidCredentialsError("Invalid email or password")

        self.access_control_service.ensure_can_get_all_users(current_user)

        return await self.user_repository.get_all(page, size)

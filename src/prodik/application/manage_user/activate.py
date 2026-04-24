from dataclasses import dataclass

from prodik.application.errors import (
    UserNotFoundError,
)
from prodik.application.interfaces.repositories import (
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import SessionService
from prodik.domain.user import UserId
from prodik.domain.user.services import AccessControlService


@dataclass
class ActivateUserInteractor:
    session_service: SessionService
    access_control_service: AccessControlService
    user_repository: UserRepository
    tx_manager: TransactionManager

    async def execute(self, target_id: UserId) -> None:
        async with self.tx_manager:
            auth_meta = await self.session_service.get_authorized_meta()

            self.access_control_service.ensure_can_moderate_users(auth_meta.user)

            target_user = await self.user_repository.get_by_uuid(target_id)
            if target_user is None:
                raise UserNotFoundError("User not found")

            target_user.activate()
            await self.user_repository.update(target_user)

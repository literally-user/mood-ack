from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.manage_user.errors import UserNotFoundError
from prodik.application.services import SessionService
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
    session_service: SessionService
    access_control_service: AccessControlService
    user_repository: UserRepository
    tx_manager: TransactionManager

    async def execute(
        self, request: UpdateProfileRequestDTO, target_id: UserId
    ) -> None:
        async with self.tx_manager:
            auth_meta = await self.session_service.get_authorized_meta()

            if auth_meta.user.id == target_id:
                target_user = auth_meta.user
            else:
                target_user = await self.user_repository.get_by_uuid(target_id)  # type: ignore
                if target_user is None:
                    raise UserNotFoundError("User not found")

            self.access_control_service.ensure_can_update_profile(
                auth_meta.user, target_user
            )

            target_user.update_profile(
                request.age,
                request.first_name,
                request.last_name,
                request.email,
                request.username,
            )

            await self.user_repository.update(target_user)

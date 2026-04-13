from dataclasses import dataclass

from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.errors import NotEnoughRightsError, ModeratorCannotBeDeactivated, UserNotFoundError
from prodik.domain.user import UserId


@dataclass
class DeactivateUserInteractor:
    idp: IdentityProvider
    user_repository: UserRepository
    tx_manager: TransactionManager

    async def execute(self, target_id: UserId) -> None:
        async with self.tx_manager:
            current_user = await self.idp.get_current_user()
            if not current_user.can_manage_users():
                raise NotEnoughRightsError("Not enough rights to perform operation")
            
            if current_user.id == target_id:
                raise ModeratorCannotBeDeactivated("Moderator cannot be deactivated")

            target_user = await self.user_repository.get_by_uuid(target_id)
            if target_user is None:
                raise UserNotFoundError("User not found")

            target_user.deactivate()
            await self.user_repository.update(target_user)
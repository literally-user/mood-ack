from dataclasses import dataclass

from prodik.application.errors import (
    NotEnoughRightsError,
    UserNotFoundError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.user import UserId


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateProfileRequestDTO:
    email: str | None
    first_name: str | None
    last_name: str | None
    age: int | None
    username: str | None


@dataclass
class UpdateProfileInteractor:
    user_repository: UserRepository
    tx_manager: TransactionManager
    idp: IdentityProvider

    async def execute(
        self, request: UpdateProfileRequestDTO, target_id: UserId
    ) -> None:
        async with self.tx_manager:
            current_user_session = await self.idp.get_current_session()
            if current_user_session.is_revoked():
                UserSessionRevokedError("Session was revoked")
            current_user = await self.idp.get_current_user()
            if not current_user.can_manage_users() and current_user.id != target_id:
                raise NotEnoughRightsError("Not enough rights to perform operation")

            if current_user.id == target_id:
                target_user = current_user
            else:
                target_user = await self.user_repository.get_by_uuid(target_id)  # type: ignore
                if target_user is None:
                    raise UserNotFoundError("User not found")

            if request.age is not None:
                target_user.change_age(request.age)
            if request.first_name is not None:
                target_user.change_first_name(request.first_name)
            if request.last_name is not None:
                target_user.change_last_name(request.last_name)
            if request.email is not None:
                target_user.change_email(request.email)
            if request.username is not None:
                target_user.change_username(request.username)

            await self.user_repository.update(target_user)

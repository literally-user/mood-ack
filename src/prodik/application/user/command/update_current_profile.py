from dataclasses import dataclass

from prodik.application.errors import UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.application.interfaces.transaction_manager import TransactionManager


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateCurrentProfileRequestDTO:
    email: str | None
    first_name: str | None
    last_name: str | None
    age: int | None
    username: str | None


@dataclass
class UpdateCurrentProfileInteractor:
    user_repository: UserRepository
    tx_manager: TransactionManager
    idp: IdentityProvider

    async def execute(self, request: UpdateCurrentProfileRequestDTO) -> None:
        async with self.tx_manager:
            current_user_session = await self.idp.get_current_session()
            if current_user_session.is_revoked():
                raise UserSessionRevokedError("Session was revoked")
            current_user = await self.idp.get_current_user()

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

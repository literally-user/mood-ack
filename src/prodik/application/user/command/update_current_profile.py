from dataclasses import dataclass

from prodik.application.interfaces.repositories import (
    UserRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.application.services import SessionService


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateCurrentProfileRequestDTO:
    email: str | None
    first_name: str | None
    last_name: str | None
    age: int | None
    username: str | None


@dataclass
class UpdateCurrentProfileInteractor:
    session_service: SessionService
    user_repository: UserRepository
    tx_manager: TransactionManager

    async def execute(self, request: UpdateCurrentProfileRequestDTO) -> None:
        async with self.tx_manager:
            auth_meta = await self.session_service.get_authorized_meta()

            auth_meta.user.update_profile(
                request.age,
                request.first_name,
                request.last_name,
                request.email,
                request.username,
            )

            await self.user_repository.update(auth_meta.user)

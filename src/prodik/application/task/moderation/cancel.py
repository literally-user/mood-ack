from dataclasses import dataclass

from prodik.application.errors import (
    InvalidCredentialsError,
    TaskNotFoundError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    TaskRepository,
    UserRepository,
    UserSessionRepository,
)
from prodik.application.interfaces.transaction_manager import TransactionManager
from prodik.domain.credentials import IP
from prodik.domain.task import TaskId
from prodik.domain.user.services import AccessControlService


@dataclass
class CancelTaskInteractor:
    idp: IdentityProvider
    task_repository: TaskRepository
    access_control_service: AccessControlService
    user_session_repository: UserSessionRepository
    user_repository: UserRepository
    tx_manager: TransactionManager

    async def execute(self, task_id: TaskId) -> None:
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

            task = await self.task_repository.get_by_id(task_id)
            if task is None:
                raise TaskNotFoundError("Task not found")

            self.access_control_service.ensure_can_moderate_task(current_user, task)

            task.deprecate()
            await self.task_repository.update(task)

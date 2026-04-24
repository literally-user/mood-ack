from dataclasses import dataclass

from prodik.application.errors import NotEnoughRightsError
from prodik.domain.task import Task
from prodik.domain.user import User


@dataclass
class AccessControlService:
    def ensure_can_update_profile(self, caller: User, target: User) -> None:
        if not caller.can_manage_users() and caller != target:
            raise NotEnoughRightsError("Not enough rights to perform operation")

    def ensure_can_get_all_users(self, caller: User) -> None:
        if not caller.can_manage_users():
            raise NotEnoughRightsError("Not enough rights to perform operation")

    def ensure_can_moderate_users(self, caller: User) -> None:
        if not caller.can_manage_users():
            raise NotEnoughRightsError("Not enough rights to perform operation")

    def ensure_can_get_task(self, caller: User, task: Task) -> None:
        if not caller.can_manage_tasks() and caller.id != task.owner_id:
            raise NotEnoughRightsError("Not enough rights to perform operation")

    def ensure_can_get_all_tasks(self, caller: User) -> None:
        if not caller.can_manage_tasks():
            raise NotEnoughRightsError("Not enough rights to perform operation")

    def ensure_can_moderate_task(self, caller: User, task: Task) -> None:
        if not caller.can_manage_tasks() and caller.id != task.owner_id:
            raise NotEnoughRightsError("Not enough rights to perform operation")

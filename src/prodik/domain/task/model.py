from dataclasses import dataclass
from enum import StrEnum
from typing import Final, NewType
from uuid import UUID
from datetime import datetime, UTC

from prodik.domain.shared import Entity, ValueObject
from prodik.domain.task.errors import (
    CannotDeprecateFinishedTaskError,
    TaskResultGreaterThanError,
    TaskResultLessThanError,
)
from prodik.domain.user import User, UserId

MAX_ALLOWED_TASK_RESULT: Final[float] = 1.0
MIN_ALLOWED_TASK_RESULT: Final[float] = 0.0

TaskId = NewType("TaskId", UUID)
FileId = NewType("FileId", UUID)


class TaskState(StrEnum):
    PENDING = "PENDING"
    DONE = "DONE"
    DEPRECATED = "DEPRECATED"


class FileInput(ValueObject[FileId]):
    def __init__(self, value: FileId) -> None:
        super().__init__(value)


class RawInput(ValueObject[str]):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class TaskResult(ValueObject[float]):
    def __init__(self, value: float) -> None:
        if value > 1.0:
            raise TaskResultGreaterThanError(
                f"Task result cannot be greater than {MAX_ALLOWED_TASK_RESULT}"
            )
        if value < 0.0:
            raise TaskResultLessThanError(
                f"Task result cannot be less than {MIN_ALLOWED_TASK_RESULT}"
            )
        super().__init__(value)


@dataclass
class Task(Entity[TaskId]):
    _owner_id: UserId
    _state: TaskState
    _input: FileInput | RawInput
    _result: TaskResult | None

    @classmethod
    def new(cls, id: TaskId, owner: User, input: FileInput | RawInput) -> "Task":
        now = datetime.now(tz=UTC)
        return Task(
            _id=id,
            _owner_id=owner.id,
            _state=TaskState.PENDING,
            _input=input,
            _result=None,
            _created_at=now,
            _updated_at=now,
        )

    @property
    def state(self) -> TaskState:
        return self._state

    def deprecate(self) -> None:
        if self._state == TaskState.DONE:
            raise CannotDeprecateFinishedTaskError("Finished task cannot be deprecated")

    def set_result(self, result: float) -> None:
        self._result = TaskResult(result)
        self._state = TaskState.DONE

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, NewType
from uuid import UUID

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
FileInputId = NewType("FileInputId", UUID)
RawInputId = NewType("RawInputId", UUID)


class TaskState(StrEnum):
    DEPRECATED = "DEPRECATED"
    PENDING = "PENDING"
    DONE = "DONE"


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


class InputType(StrEnum):
    FILE = "FILE"
    RAW = "RAW"


@dataclass
class FileInput(Entity[FileInputId]):
    file_id: FileId

    @classmethod
    def new(cls, id: FileInputId, file_id: FileId) -> "FileInput":
        now = datetime.now(tz=UTC)
        return FileInput(
            id=id,
            file_id=file_id,
            created_at=now,
            updated_at=now,
        )


@dataclass
class RawInput(Entity[RawInputId]):
    content: str

    @classmethod
    def new(cls, id: RawInputId, content: str) -> "RawInput":
        now = datetime.now(tz=UTC)
        return RawInput(
            id=id,
            content=content,
            created_at=now,
            updated_at=now,
        )


@dataclass
class Task(Entity[TaskId]):
    owner_id: UserId
    state: TaskState
    input_type: InputType
    input_id: RawInputId | FileInputId
    result: TaskResult | None

    @classmethod
    def new(cls, id: TaskId, owner: User, input: FileInput | RawInput) -> "Task":
        now = datetime.now(tz=UTC)
        return Task(
            id=id,
            owner_id=owner.id,
            state=TaskState.PENDING,
            input_type=InputType.FILE
            if isinstance(input, FileInput)
            else InputType.RAW,
            input_id=input.id,
            result=None,
            created_at=now,
            updated_at=now,
        )

    def deprecate(self) -> None:
        if self.state == TaskState.DONE:
            raise CannotDeprecateFinishedTaskError("Finished task cannot be deprecated")
        self.state = TaskState.DEPRECATED
        self.touch()

    def set_result(self, result: float) -> None:
        self.result = TaskResult(result)
        self.state = TaskState.DONE
        self.touch()

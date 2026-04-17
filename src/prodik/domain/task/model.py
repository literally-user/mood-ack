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
    _file_id: FileId

    @classmethod
    def new(cls, id: FileInputId, file_id: FileId) -> "FileInput":
        now = datetime.now(tz=UTC)
        return FileInput(
            _id=id,
            _file_id=file_id,
            _created_at=now,
            _updated_at=now,
        )

    @property
    def id(self) -> FileInputId:
        return self._id


@dataclass
class RawInput(Entity[RawInputId]):
    _content: str

    @classmethod
    def new(cls, id: RawInputId, content: str) -> "RawInput":
        now = datetime.now(tz=UTC)
        return RawInput(
            _id=id,
            _content=content,
            _created_at=now,
            _updated_at=now,
        )

    @property
    def id(self) -> RawInputId:
        return self._id


@dataclass
class Task(Entity[TaskId]):
    _owner_id: UserId
    _state: TaskState
    _input_type: InputType
    _input_id: RawInputId | FileInputId
    _result: TaskResult | None

    @classmethod
    def new(cls, id: TaskId, owner: User, input: FileInput | RawInput) -> "Task":
        now = datetime.now(tz=UTC)
        return Task(
            _id=id,
            _owner_id=owner.id,
            _state=TaskState.PENDING,
            _input_type=InputType.FILE
            if isinstance(input, FileInput)
            else InputType.RAW,
            _input_id=input.id,
            _result=None,
            _created_at=now,
            _updated_at=now,
        )

    @property
    def id(self) -> TaskId:
        return self._id

    @property
    def state(self) -> TaskState:
        return self._state

    def deprecate(self) -> None:
        if self._state == TaskState.DONE:
            raise CannotDeprecateFinishedTaskError("Finished task cannot be deprecated")
        self._state = TaskState.DEPRECATED
        self.touch()

    def set_result(self, result: float) -> None:
        self._result = TaskResult(result)
        self._state = TaskState.DONE
        self.touch()

    @property
    def owner_id(self) -> UserId:
        return self._owner_id

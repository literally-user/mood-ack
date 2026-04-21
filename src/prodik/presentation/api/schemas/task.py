from datetime import datetime

from pydantic import BaseModel

from prodik.domain.task import (
    FileInputId,
    InputType,
    RawInputId,
    TaskId,
    TaskState,
)
from prodik.domain.user import UserId


class TaskSchema(BaseModel):
    id: TaskId
    owner_id: UserId
    state: TaskState
    input_type: InputType
    input_id: RawInputId | FileInputId
    result: float | None
    created_at: datetime
    updated_at: datetime

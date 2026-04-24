from typing import Protocol

from prodik.domain.task import TaskId


class RawProcessor(Protocol):
    def process(self, task_id: TaskId, content: str) -> None: ...

from typing import Protocol

from prodik.domain.task import Task


class TaskProcessor(Protocol):
    def process(self, content: str, task: Task) -> None: ...

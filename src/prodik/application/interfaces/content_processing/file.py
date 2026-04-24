from typing import Protocol

from prodik.domain.task import FileId, TaskId


class FileProcessor(Protocol):
    def process(self, task_id: TaskId, file_id: FileId) -> None: ...

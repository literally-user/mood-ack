from types import TracebackType

from prodik.domain.task import Task


class HandleExecutionContext:
    task: Task

    def __init__(self, task: Task) -> None:
        self.task = task

    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc:
            self.task.deprecate()
            return

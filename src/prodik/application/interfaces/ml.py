from typing import Protocol

from prodik.domain.task import Task


class PredictingModel(Protocol):
    def get_model_info(self) -> None: ...
    def process(self, text: str, task: Task) -> None: ...

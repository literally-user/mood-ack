from dataclasses import dataclass
from typing import Protocol

from prodik.domain.task import Task


@dataclass
class ModelMeta:
    version: str
    nickname: str


class PredictingModel(Protocol):
    def get_model_info(self) -> ModelMeta: ...
    def process(self, text: str, task: Task) -> float: ...

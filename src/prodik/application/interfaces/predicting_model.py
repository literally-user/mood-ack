from dataclasses import dataclass
from typing import Protocol


@dataclass
class ModelMeta:
    version: str
    nickname: str


class PredictingModel(Protocol):
    def get_model_info(self) -> ModelMeta: ...
    def process(self, text: str) -> float: ...

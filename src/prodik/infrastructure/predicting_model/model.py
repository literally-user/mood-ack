from dataclasses import dataclass

from prodik.application.interfaces.predicting_model import ModelMeta, PredictingModel


@dataclass
class PredictingModelImpl(PredictingModel):
    def get_model_info(self) -> ModelMeta:
        return ModelMeta(nickname="Coming Soon", version="0.0.0")

    def process(self, text: str) -> float:  # noqa: ARG002 - coming soon
        return 0.5

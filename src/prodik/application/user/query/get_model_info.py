from dataclasses import dataclass

from prodik.application.interfaces.ml import PredictingModel, ModelMeta

@dataclass
class GetPredictingModelInfo:
    predicting_model: PredictingModel

    def execute(self) -> ModelMeta:
        return self.predicting_model.get_model_info()
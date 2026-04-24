from dataclasses import dataclass

from prodik.application.interfaces.predicting_model import ModelMeta, PredictingModel
from prodik.application.services import SessionService


@dataclass
class GetPredictingModelInfoInteractor:
    predicting_model: PredictingModel
    session_service: SessionService

    async def execute(self) -> ModelMeta:
        await self.session_service.get_authorized_meta()

        return self.predicting_model.get_model_info()

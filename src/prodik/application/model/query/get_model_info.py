from dataclasses import dataclass

from prodik.application.errors import UserSessionRevokedError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.predicting_model import ModelMeta, PredictingModel


@dataclass
class GetPredictingModelInfoInteractor:
    predicting_model: PredictingModel
    idp: IdentityProvider

    async def execute(self) -> ModelMeta:
        current_user_session = await self.idp.get_current_session()
        if current_user_session.is_revoked():
            raise UserSessionRevokedError("Session was revoked")
        return self.predicting_model.get_model_info()

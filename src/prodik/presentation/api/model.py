from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.model.query import GetPredictingModelInfoInteractor
from prodik.presentation.api.schemas.model import GetModelInfoResponse

router = APIRouter(tags=["model"], prefix="/model", route_class=DishkaRoute)


@router.get("/")
async def get_model_info(
    interactor: FromDishka[GetPredictingModelInfoInteractor],
) -> GetModelInfoResponse:
    result = await interactor.execute()
    return GetModelInfoResponse(version=result.version, nickname=result.nickname)

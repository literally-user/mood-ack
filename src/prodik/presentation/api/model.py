from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from prodik.application.content_processing import ProcessRawInteractor
from prodik.application.model.query import GetPredictingModelInfoInteractor
from prodik.presentation.api.schemas.model import (
    GetModelInfoResponse,
    ProcessRawContentRequest,
)
from prodik.presentation.api.schemas.task import TaskSchema

router = APIRouter(tags=["model"], prefix="/model", route_class=DishkaRoute)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_model_info(
    interactor: FromDishka[GetPredictingModelInfoInteractor],
) -> GetModelInfoResponse:
    result = await interactor.execute()
    return GetModelInfoResponse(version=result.version, nickname=result.nickname)


@router.post("/process/raw", status_code=status.HTTP_202_ACCEPTED)
async def process_raw_content(
    request: ProcessRawContentRequest, interactor: FromDishka[ProcessRawInteractor]
) -> TaskSchema:
    task = await interactor.execute(request.text)
    return TaskSchema(
        id=task.id,
        owner_id=task.owner_id,
        state=task.state,
        input_type=task.input_type,
        input_id=task.input_id,
        result=task.result.value if task.result is not None else None,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )

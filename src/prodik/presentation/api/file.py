from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from prodik.application.content_processing import ProcessFileInteractor
from prodik.application.file.query import GetFileStorageLinkInteractor
from prodik.domain.task import FileId
from prodik.presentation.api.schemas.task import TaskSchema

router = APIRouter(tags=["files"], prefix="/files", route_class=DishkaRoute)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_upload_file_link(
    filename: str, interactor: FromDishka[GetFileStorageLinkInteractor]
) -> str:
    return await interactor.execute(filename)


@router.post("/completed/{target_id}", status_code=status.HTTP_200_OK)
async def process_file(
    target_id: FileId, interactor: FromDishka[ProcessFileInteractor]
) -> TaskSchema:
    task = await interactor.execute(target_id)
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

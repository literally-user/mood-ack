from http import HTTPStatus

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.task.query import (
    GetAllTasksByUserInteractor,
    GetAllTasksInteractor,
    GetTaskInteractor,
)
from prodik.domain.task import TaskId
from prodik.presentation.api.schemas.task import TaskSchema

router = APIRouter(tags=["tasks"], prefix="/tasks", route_class=DishkaRoute)


@router.get("/", status_code=HTTPStatus.OK)
async def get_tasks(
    page: int, size: int, interactor: FromDishka[GetAllTasksInteractor]
) -> list[TaskSchema]:
    result = await interactor.execute(page, size)
    return [
        TaskSchema(
            id=task.id,
            owner_id=task.owner_id,
            state=task.state,
            input_type=task.input_type,
            input_id=task.input_id,
            result=task.result.value if task.result is not None else None,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in result
    ]


@router.get("/me", status_code=HTTPStatus.OK)
async def get_tasks_by_user(
    page: int, size: int, interactor: FromDishka[GetAllTasksByUserInteractor]
) -> list[TaskSchema]:
    result = await interactor.execute(page, size)
    return [
        TaskSchema(
            id=task.id,
            owner_id=task.owner_id,
            state=task.state,
            input_type=task.input_type,
            input_id=task.input_id,
            result=task.result.value if task.result is not None else None,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in result
    ]


@router.get("/{target_id}", status_code=HTTPStatus.OK)
async def get_task(
    target_id: TaskId, interactor: FromDishka[GetTaskInteractor]
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

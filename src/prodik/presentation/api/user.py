from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from prodik.application.user.command.change_password import (
    ChangePasswordInteractor,
    ChangePasswordRequestDTO,
)
from prodik.presentation.api.schemas.auth import AuthResponse
from prodik.presentation.api.schemas.user import ChangePasswordRequest

router = APIRouter(tags=["users"], prefix="/users", route_class=DishkaRoute)


@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest, interactor: FromDishka[ChangePasswordInteractor]
) -> AuthResponse:
    result = await interactor.execute(
        ChangePasswordRequestDTO(
            old_password=request.old_password,
            new_password=request.new_password,
        )
    )
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )

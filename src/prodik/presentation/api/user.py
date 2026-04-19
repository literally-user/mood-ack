from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from prodik.application.user.command import (
    ChangePasswordInteractor,
    ChangePasswordRequestDTO,
    UpdateCurrentProfileInteractor,
    UpdateCurrentProfileRequestDTO,
)
from prodik.presentation.api.schemas.auth import AuthResponse
from prodik.presentation.api.schemas.user import (
    ChangePasswordRequest,
    UpdateCurrentProfileRequest,
)

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


@router.put("/me/profile", status_code=status.HTTP_204_NO_CONTENT)
async def update_current_profile(
    request: UpdateCurrentProfileRequest,
    interactor: FromDishka[UpdateCurrentProfileInteractor],
) -> None:
    await interactor.execute(
        UpdateCurrentProfileRequestDTO(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            age=request.age,
            username=request.username,
        )
    )

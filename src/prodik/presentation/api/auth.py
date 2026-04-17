from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.user.command import (
    RegisterInteractor,
    RegisterRequestDTO,
)
from prodik.presentation.api.schemas.auth import (
    AuthResponse,
    RegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["authorization"], route_class=DishkaRoute)


@router.post("/register")
async def register(
    request: RegisterRequest, interactor: FromDishka[RegisterInteractor]
) -> AuthResponse:
    result = await interactor.execute(
        RegisterRequestDTO(
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=request.password,
            age=request.age,
        )
    )
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.user.command import (
    RegisterInteractor,
    LoginInteractor,
    RegisterRequestDTO,
    LoginRequestDTO,
)
from prodik.presentation.api.schemas.auth import (
    AuthResponse,
    RegisterRequest,
    LoginRequest,
)

router = APIRouter(prefix="/auth", tags=["authorization"], route_class=DishkaRoute)


@router.post("/register", status_code=201)
async def register(
    request: RegisterRequest, interactor: FromDishka[RegisterInteractor]
) -> AuthResponse:
    result = await interactor.execute(
        RegisterRequestDTO(
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=request.password.get_secret_value(),
            age=request.age,
        )
    )
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )

@router.post("/login", status_code=200)
async def login(
    request: LoginRequest,
    interactor: FromDishka[LoginInteractor],
) -> AuthResponse:
    result = await interactor.execute(LoginRequestDTO(
        password=request.password.get_secret_value(),
        email=request.email,
    ))
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from prodik.application.authorization import (
    ChangePasswordInteractor,
    ChangePasswordRequestDTO,
    LoginInteractor,
    LoginRequestDTO,
    OAuthLoginInteractor,
    RefreshTokenInteractor,
    RegisterInteractor,
    RegisterRequestDTO,
)
from prodik.presentation.api.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    OAuthRequest,
    RefreshTokenRequest,
    RegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["authorization"], route_class=DishkaRoute)


@router.post("/register", status_code=status.HTTP_201_CREATED)
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


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    interactor: FromDishka[LoginInteractor],
) -> AuthResponse:
    result = await interactor.execute(
        LoginRequestDTO(
            password=request.password.get_secret_value(),
            email=request.email,
        )
    )
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    request: RefreshTokenRequest,
    interactor: FromDishka[RefreshTokenInteractor],
) -> AuthResponse:
    result = await interactor.execute(request.refresh_token)
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )


@router.post("/callback/sso", status_code=status.HTTP_200_OK)
async def callback_sso(
    request: OAuthRequest, interactor: FromDishka[OAuthLoginInteractor]
) -> AuthResponse:
    result = await interactor.execute(request.code, request.state)
    return AuthResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
    )


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

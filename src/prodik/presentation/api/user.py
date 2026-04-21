from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from prodik.application.user.command import (
    ChangePasswordInteractor,
    ChangePasswordRequestDTO,
    UpdateCurrentProfileInteractor,
    UpdateCurrentProfileRequestDTO,
    UpdateProfileInteractor,
    UpdateProfileRequestDTO,
)
from prodik.application.user.moderation import (
    ActivateUserInteractor,
    DeactivateUserInteractor,
)
from prodik.application.user.query import (
    GetAllUsersInteractor,
    GetCurrentProfileInteractor,
    GetUserProfileInteractor,
)
from prodik.domain.user import UserId
from prodik.presentation.api.schemas.auth import AuthResponse
from prodik.presentation.api.schemas.user import (
    ChangePasswordRequest,
    UpdateProfileRequest,
    UserSchema,
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
    request: UpdateProfileRequest,
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


@router.put("/{target_id}/profile", status_code=status.HTTP_204_NO_CONTENT)
async def update_profile(
    target_id: UserId,
    request: UpdateProfileRequest,
    interactor: FromDishka[UpdateProfileInteractor],
) -> None:
    await interactor.execute(
        UpdateProfileRequestDTO(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            age=request.age,
            username=request.username,
        ),
        target_id,
    )


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    target_id: UserId, interactor: FromDishka[DeactivateUserInteractor]
) -> None:
    await interactor.execute(target_id)


@router.post("/{target_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def activate_user(
    target_id: UserId, interactor: FromDishka[ActivateUserInteractor]
) -> None:
    await interactor.execute(target_id)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_profile(
    interactor: FromDishka[GetCurrentProfileInteractor],
) -> UserSchema:
    result = await interactor.execute()
    return UserSchema(
        id=result.id,
        username=result.username.value,
        first_name=result.first_name.value,
        last_name=result.last_name.value,
        email=result.email.value,
        age=result.age.value,
        role=result.role,
        status=result.status,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get("/{target_id}", status_code=status.HTTP_200_OK)
async def get_user_profile(
    target_id: UserId, interactor: FromDishka[GetUserProfileInteractor]
) -> UserSchema:
    result = await interactor.execute(target_id)
    return UserSchema(
        id=result.id,
        username=result.username.value,
        first_name=result.first_name.value,
        last_name=result.last_name.value,
        email=result.email.value,
        age=result.age.value,
        role=result.role,
        status=result.status,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get("/{page}/{size}", status_code=status.HTTP_200_OK)
async def get_all_users(
    page: int,
    size: int,
    interactor: FromDishka[GetAllUsersInteractor]
) -> list[UserSchema]:
    result = await interactor.execute(page, size)
    return [
        UserSchema(
            id=x.id,
            username=x.username.value,
            first_name=x.first_name.value,
            last_name=x.last_name.value,
            email=x.email.value,
            age=x.age.value,
            role=x.role,
            status=x.status,
            created_at=x.created_at,
            updated_at=x.updated_at,
        )
        for x in result
    ]

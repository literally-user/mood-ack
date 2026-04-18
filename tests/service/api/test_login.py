import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import AsyncContainer
from sqlalchemy import delete

from tests.service.factories import TestUserInformation

from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.credentials import LocalAuthorization


@pytest.mark.asyncio
async def test_login_ok(test_client: AsyncClient, test_user_info: TestUserInformation) -> None:
    response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=3600,
    )

@pytest.mark.asyncio
async def test_login_invalid_email(test_client: AsyncClient, test_user_info: TestUserInformation) -> None:
    response = await test_client.post(
        "/auth/login",
        json={
            "email": "invalidemail@literally.op",
            "password": test_user_info.password,
        }
    )

    assert response.status_code == 401
    assert response.json() == IsPartialDict(
        detail="Invalid email or password"
    )

@pytest.mark.asyncio
async def test_login_invalid_password(test_client: AsyncClient, test_user_info: TestUserInformation) -> None:
    response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": "InvalidPassword",
        }
    )

    assert response.status_code == 401
    assert response.json() == IsPartialDict(
        detail="Invalid email or password"
    )

@pytest.mark.asyncio
async def test_login_deactivated(test_client: AsyncClient, test_user_info: TestUserInformation, test_container: AsyncContainer) -> None:
    async with test_container() as container:
        user_repository = await container.get(UserRepository)
    
    test_user_info.user.deactivate()
    await user_repository.update(test_user_info.user)

    response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    assert response.status_code == 403
    assert response.json() == IsPartialDict(
        detail="User deactivated"
    )

@pytest.mark.asyncio
async def test_login_local_auth_not_found(test_client: AsyncClient, test_user_info: TestUserInformation, test_session: AsyncSession) -> None:
    await test_session.execute(
        delete(
            LocalAuthorization
        ).where(
            LocalAuthorization.id == test_user_info.local_authorization.id # type: ignore
       )
    )

    response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    assert response.status_code == 401
    assert response.json() == IsPartialDict(
        detail="Invalid email or password"
    )
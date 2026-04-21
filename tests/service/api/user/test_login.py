from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from tests.service.factories import UserFactory

from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.credentials import LocalAuthorization


@pytest.mark.asyncio
async def test_login_ok(test_client: AsyncClient, test_user_factory: UserFactory) -> None:
    user = await test_user_factory.create_user_info()

    response = await test_client.post(
        "/auth/login",
        json={
            "email": user.user.email.value,
            "password": user.password,
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=3600,
    )

@pytest.mark.asyncio
async def test_login_invalid_email(test_client: AsyncClient, test_user_factory: UserFactory) -> None:
    user = await test_user_factory.create_user_info()

    response = await test_client.post(
        "/auth/login",
        json={
            "email": "invalidemail@literally.op",
            "password": user.password,
        }
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid email or password"
    )

@pytest.mark.asyncio
async def test_login_invalid_password(test_client: AsyncClient, test_user_factory: UserFactory) -> None:
    user = await test_user_factory.create_user_info()
    response = await test_client.post(
        "/auth/login",
        json={
            "email": user.user.email.value,
            "password": "InvalidPassword",
        }
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid email or password"
    )

@pytest.mark.asyncio
async def test_login_deactivated(test_client: AsyncClient, user_repository: UserRepository, test_user_factory: UserFactory) -> None:
    user = await test_user_factory.create_user_info()
    user.user.deactivate()
    await user_repository.update(user.user)

    response = await test_client.post(
        "/auth/login",
        json={
            "email": user.user.email.value,
            "password": user.password,
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="User deactivated"
    )

@pytest.mark.asyncio
async def test_login_local_auth_not_found(
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_user_factory: UserFactory
) -> None:
    user = await test_user_factory.create_user_info()

    await test_session.execute(
        delete(
            LocalAuthorization
        ).where(
            LocalAuthorization.id == user.local_authorization.id # type: ignore
       )
    )

    response = await test_client.post(
        "/auth/login",
        json={
            "email": user.user.email.value,
            "password": user.password,
        }
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid email or password"
    )
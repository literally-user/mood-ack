import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import AsyncContainer
from sqlalchemy import delete

from prodik.application.interfaces.repositories import UserSessionRepository
from tests.service.factories import TestUserInformation
from prodik.domain.credentials import LocalAuthorization

@pytest.mark.asyncio
async def test_change_password_ok(test_client: AsyncClient, test_user_info: TestUserInformation) -> None:
    response = await test_client.put(
        "/users/password",
        json={
            "old_password": test_user_info.password,
            "new_password": "NewPassword123"
        },
        headers={
            "Authorization": f"Bearer {test_user_info.access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=3600
    )

@pytest.mark.asyncio
async def test_change_password_session_revoked(
    test_client: AsyncClient,
    test_user_info: TestUserInformation,
    user_session_repository: UserSessionRepository,
) -> None:
    test_user_info.user_session.revoke()
    await user_session_repository.update(test_user_info.user_session)

    response = await test_client.put(
        "/users/password",
        json={
            "old_password": test_user_info.password,
            "new_password": "NewPassword123"
        },
        headers={
            "Authorization": f"Bearer {test_user_info.access_token}"
        }
    )

    assert response.status_code == 401
    assert response.json() == IsPartialDict(
        detail="Invalid authorization header format"
    )

@pytest.mark.asyncio
async def test_change_password_local_auth_not_found(
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_user_info: TestUserInformation,
) -> None:
    await test_session.execute(
        delete(
            LocalAuthorization
        ).where(
            LocalAuthorization.id == test_user_info.local_authorization.id # type: ignore
        )
    )

    response = await test_client.put(
        "/users/password",
        json={
            "old_password": test_user_info.password,
            "new_password": "NewPassword123"
        },
        headers={
            "Authorization": f"Bearer {test_user_info.access_token}"
        }
    )

    assert response.status_code == 401
    assert response.json() == IsPartialDict(
        detail="Invalid authorization header format"
    )

@pytest.mark.asyncio
async def test_change_password_wrong_old_password(
    test_client: AsyncClient,
    test_user_info: TestUserInformation,
) -> None:

    response = await test_client.put(
        "/users/password",
        json={
            "old_password": "TotallyWrongPassowrd",
            "new_password": "NewPassword123"
        },
        headers={
            "Authorization": f"Bearer {test_user_info.access_token}"
        }
    )

    assert response.status_code == 401
    assert response.json() == IsPartialDict(
        detail="Wrong old password"
    )

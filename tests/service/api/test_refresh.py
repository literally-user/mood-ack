from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import AsyncContainer
from sqlalchemy import delete


from tests.service.factories import TestUserInformation

from prodik.application.interfaces.repositories import UserSessionRepository
from prodik.domain.user import User

@pytest.mark.asyncio
async def test_refresh_token_ok(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    response = await test_client.post(
        '/auth/refresh',
        json={
            "refresh_token": test_user.user_session.refresh_token
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=3600,
    )


@pytest.mark.asyncio
async def test_refresh_token_session_not_found(
    test_client: AsyncClient,
) -> None:
    response = await test_client.post(
        '/auth/refresh',
        json={
            "refresh_token": "InvalidToken"
        }
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid token format"
    )

@pytest.mark.asyncio
async def test_refresh_token_session_revoked(
    test_client: AsyncClient,
    test_user: TestUserInformation,
    user_session_repository: UserSessionRepository,
) -> None:

    test_user.user_session.revoke()
    await user_session_repository.update(test_user.user_session)

    response = await test_client.post(
        '/auth/refresh',
        json={
            "refresh_token": test_user.user_session.refresh_token
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )

@pytest.mark.asyncio
async def test_refresh_token_user_not_found(
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_user: TestUserInformation,
) -> None:
    await test_session.execute(
        delete(
            User
        ).where(
            User.id == test_user.user.id # type: ignore
        )
    )
    response = await test_client.post(
        '/auth/refresh',
        json={
            "refresh_token": test_user.user_session.refresh_token
        }
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid token format"
    )
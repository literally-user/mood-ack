from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr


from tests.service.factories import UserFactory, gen_string

from prodik.application.interfaces.repositories import UserSessionRepository

@pytest.mark.asyncio
async def test_refresh_token_ok(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    user = await test_user_factory.create_user_info()

    response = await test_client.post(
        '/auth/refresh',
        json={
            "refresh_token": user.user_session.refresh_token
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
    test_user_factory: UserFactory,
    user_session_repository: UserSessionRepository,
) -> None:
    user = await test_user_factory.create_user_info()

    user.user_session.revoke()
    await user_session_repository.update(user.user_session)

    response = await test_client.post(
        '/auth/refresh',
        json={
            "refresh_token": user.user_session.refresh_token
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )

@pytest.mark.asyncio
async def test_refresh_token_user_not_found(
    test_client: AsyncClient,
) -> None:
    response = await test_client.post(
        '/auth/refresh',
        json={
            "refresh_token": gen_string(1, 50)
        }
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == IsPartialDict(
        detail="Invalid token format"
    )
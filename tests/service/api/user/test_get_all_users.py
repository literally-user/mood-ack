from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

from prodik.application.interfaces.repositories import UserSessionRepository
from tests.service.factories import UserFactory

@pytest.mark.asyncio
async def test_get_all_users_ok(
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    users = [
        await test_user_factory.create_user_info()
        for _ in range(5)
    ]
    moderator = await test_user_factory.create_moderator_info()

    response = await test_client.get(
        f'/users/{1}/{5}',
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == len(users)

@pytest.mark.asyncio
async def test_get_all_users_session_was_revoked(
    user_session_repository: UserSessionRepository,
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    moderator = await test_user_factory.create_moderator_info()

    moderator.user_session.revoke()
    await user_session_repository.update(moderator.user_session)


    response = await test_client.get(
        f'/users/{1}/{5}',
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )
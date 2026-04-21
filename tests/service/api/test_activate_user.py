from http import HTTPStatus
from uuid import uuid4

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

from prodik.application.interfaces.repositories import UserSessionRepository

from tests.service.factories import UserFactory

@pytest.mark.asyncio
async def test_update_activate_user_ok(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    target = await test_user_factory.create_user_info()
    moderator = await test_user_factory.create_moderator_info()

    response = await test_client.post(
        f"/users/{target.user.id}/activate",
        headers={
            "Authorization": f"Bearer {moderator.access_token}",
        }
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_activate_user_session_revoked(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
    user_session_repository: UserSessionRepository,
) -> None:
    target = await test_user_factory.create_user_info()
    moderator = await test_user_factory.create_moderator_info()

    moderator.user_session.revoke()
    await user_session_repository.update(moderator.user_session)

    response = await test_client.post(
        f"/users/{target.user.id}/activate",
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )

@pytest.mark.asyncio
async def test_update_activate_user_not_enough_rights(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    user = await test_user_factory.create_user_info()
    target = await test_user_factory.create_user_info()

    response = await test_client.post(
        f"/users/{target.user.id}/activate",
        headers={
            "Authorization": f"Bearer {user.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation"
    )


@pytest.mark.asyncio
async def test_update_activate_user_user_not_found(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    moderator = await test_user_factory.create_moderator_info()

    response = await test_client.post(
        f"/users/{uuid4()}/activate",
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="User not found"
    )

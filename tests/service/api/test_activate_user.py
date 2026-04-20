from http import HTTPStatus
from uuid import uuid4

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

from prodik.application.interfaces.repositories import UserSessionRepository

from tests.service.factories import TestUserInformation

@pytest.mark.asyncio
async def test_update_activate_user_ok(
    test_client: AsyncClient,
    test_moderator: TestUserInformation,
    test_user: TestUserInformation,
) -> None:
    response = await test_client.post(
        f"/users/{test_user.user.id}/activate",
        headers={
            "Authorization": f"Bearer {test_moderator.access_token}",
        }
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_activate_user_session_revoked(
    test_client: AsyncClient,
    user_session_repository: UserSessionRepository,
    test_moderator: TestUserInformation,
    test_user: TestUserInformation,
) -> None:
    test_moderator.user_session.revoke()
    await user_session_repository.update(test_moderator.user_session)

    response = await test_client.post(
        f"/users/{test_user.user.id}/activate",
        headers={
            "Authorization": f"Bearer {test_moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )

@pytest.mark.asyncio
async def test_update_activate_user_not_enough_rights(
    test_client: AsyncClient,
    test_moderator: TestUserInformation,
    test_user: TestUserInformation,
) -> None:

    response = await test_client.post(
        f"/users/{test_moderator.user.id}/activate",
        headers={
            "Authorization": f"Bearer {test_user.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation"
    )


@pytest.mark.asyncio
async def test_update_activate_user_user_not_found(
    test_client: AsyncClient,
    test_moderator: TestUserInformation
) -> None:
    response = await test_client.post(
        f"/users/{uuid4()}/activate",
        headers={
            "Authorization": f"Bearer {test_moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="User not found"
    )

from http import HTTPStatus
from uuid import uuid4

import pytest
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict
from dishka import AsyncContainer

from prodik.application.interfaces.repositories import UserRepository, UserSessionRepository

from tests.service.factories import create_user_info, TestUserInformation

@pytest.mark.asyncio
async def test_update_deactivate_user_ok(
    test_client: AsyncClient,
    test_moderator: TestUserInformation,
    test_user: TestUserInformation
) -> None:
    response = await test_client.delete(
        f"/users/{test_user.user.id}",
        headers={
            "Authorization": f"Bearer {test_moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_deactivate_user_session_revoked(
    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
    user_session_repository: UserSessionRepository,
    user_repository: UserRepository
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    moderator.user.promote()
    moderator.user_session.revoke()
    await user_repository.update(moderator.user)
    await user_session_repository.update(moderator.user_session)

    response = await test_client.delete(
        f"/users/{target.user.id}",
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )

@pytest.mark.asyncio
async def test_update_deactivate_user_not_enough_rights(
    test_client: AsyncClient,
    test_user: TestUserInformation,
) -> None:
    response = await test_client.delete(
        f"/users/{test_user.user.id}",
        headers={
            "Authorization": f"Bearer {test_user.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation"
    )


@pytest.mark.asyncio
async def test_update_deactivate_user_user_not_found(
    test_client: AsyncClient,
    test_moderator: TestUserInformation,
) -> None:
    response = await test_client.delete(
        f"/users/{uuid4()}",
        headers={
            "Authorization": f"Bearer {test_moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="User not found"
    )

@pytest.mark.asyncio
async def test_update_deactivate_user_moderator_cannot_be_deactivated(
    faker: Faker,
    test_client: AsyncClient,
    test_moderator: TestUserInformation,
) -> None:
    response = await test_client.delete(
        f"/users/{test_moderator.user.id}",
        headers={
            "Authorization": f"Bearer {test_moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == IsPartialDict(
        detail="Moderator cannot be deactivated"
    )
from uuid import uuid4

import pytest
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict
from dishka import AsyncContainer

from prodik.application.interfaces.repositories import UserRepository, UserSessionRepository

from tests.service.factories import create_user_info

@pytest.mark.asyncio
async def test_update_activate_user_ok(
    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)
    
    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/users/{target.user.id}/activate",
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_update_activate_user_session_revoked(
    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_session_repository = await container.get(UserSessionRepository)
        user_repository = await container.get(UserRepository)
    
    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    moderator.user_session.revoke()
    await user_session_repository.update(moderator.user_session)

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/users/{target.user.id}/activate",
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 403
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )

@pytest.mark.asyncio
async def test_update_activate_user_not_enough_rights(
    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/users/{target.user.id}/activate",
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 403
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation"
    )


@pytest.mark.asyncio
async def test_update_activate_user_user_not_found(
    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/users/{uuid4()}/activate",
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 404
    assert response.json() == IsPartialDict(
        detail="User not found"
    )

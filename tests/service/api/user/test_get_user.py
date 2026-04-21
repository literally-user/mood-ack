from http import HTTPStatus
from uuid import uuid4

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr

from tests.service.factories import UserFactory

@pytest.mark.asyncio
async def test_get_user_ok(
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    target = await test_user_factory.create_user_info()
    moderator = await test_user_factory.create_moderator_info()

    response = await test_client.get(
        f'/users/{target.user.id}',
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        id=str(target.user.id),
        username=target.user.username.value,
        first_name=target.user.first_name.value,
        last_name=target.user.last_name.value,
        email=target.user.email.value,
        age=target.user.age.value,
        role=target.user.role.value,
        status=target.user.status.value,
        created_at=IsStr(),
        updated_at=IsStr(),
    )

@pytest.mark.asyncio
async def test_get_user_not_found(
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    moderator = await test_user_factory.create_moderator_info()

    response = await test_client.get(
        f'/users/{uuid4()}',
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="User not found"
    )
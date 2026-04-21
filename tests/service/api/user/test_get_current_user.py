from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

from tests.service.factories import UserFactory

@pytest.mark.asyncio
async def test_get_current_user_ok(
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    target = await test_user_factory.create_user_info()

    response = await test_client.get(
        f'/users/me',
        headers={
            "Authorization": f"Bearer {target.access_token}"
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
        created_at=target.user.created_at.isoformat().replace("+00:00", "Z"),
        updated_at=target.user.updated_at.isoformat().replace("+00:00", "Z"),
    )
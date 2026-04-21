from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

from tests.service.factories import UserFactory

@pytest.mark.asyncio
async def test_get_model_info_ok(
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    target = await test_user_factory.create_user_info()

    response = await test_client.get(
        f'/model/',
        headers={
            "Authorization": f"Bearer {target.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        version="0.0.0",
        nickname="Coming Soon"
    )
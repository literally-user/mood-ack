from http import HTTPStatus
import asyncio

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr, IsFloat

from tests.service.factories import UserFactory, gen_string


@pytest.mark.asyncio
async def test_process_raw_ok(
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    user = await test_user_factory.create_user_info()
    
    response = await test_client.post(
        "/model/process/raw",
        json={
            "text": gen_string(50, 100)
        },
        headers={
            "Authorization": f"Bearer {user.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json() == IsPartialDict(
        id=IsStr(),
        owner_id=str(user.user.id),
        state="PENDING",
        input_type="RAW",
        input_id=IsStr(),
        result=None,
        created_at=IsStr(),
        updated_at=IsStr(),
    )
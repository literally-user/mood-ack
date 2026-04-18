import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

@pytest.mark.asyncio
async def test_ping(test_client: AsyncClient) -> None:
    response = await test_client.get("/ping")

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        status=200
    )
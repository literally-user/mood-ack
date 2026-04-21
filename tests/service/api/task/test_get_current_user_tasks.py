from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

from tests.service.factories import UserFactory, TaskFactory

from prodik.domain.task import InputType
from prodik.application.interfaces.repositories import UserSessionRepository


@pytest.mark.asyncio
async def test_get_current_user_tasks_ok(
    test_task_factory: TaskFactory,
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    user = await test_user_factory.create_user_info()
    tasks = [
        await test_task_factory.create_done_task(
            user=user.user,
            input_type=InputType.RAW,
        ) for _ in range(5)
    ]

    response = await test_client.get(
        f'/tasks/me?page=1&size=5',
        headers={
            "Authorization": f"Bearer {user.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == len(tasks)


@pytest.mark.asyncio
async def test_get_current_user_tasks_session_was_revoked(
    user_session_repository: UserSessionRepository,
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    user = await test_user_factory.create_user_info()

    user.user_session.revoke()
    await user_session_repository.update(user.user_session)


    response = await test_client.get(
        f'/tasks/me?page=1&size=5',
        headers={
            "Authorization": f"Bearer {user.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )
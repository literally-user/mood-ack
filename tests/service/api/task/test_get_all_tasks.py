from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

from tests.service.factories import UserFactory, TaskFactory

from prodik.domain.task import InputType
from prodik.application.interfaces.repositories import UserSessionRepository


@pytest.mark.asyncio
async def test_get_all_tasks_ok(
    test_task_factory: TaskFactory,
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    moderator = await test_user_factory.create_moderator_info()
    tasks = [
        await test_task_factory.create_done_task(
            user=moderator.user,
            input_type=InputType.RAW,
        ) for _ in range(5)
    ]

    response = await test_client.get(
        f'/tasks/?page=1&size=5',
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == len(tasks)


@pytest.mark.asyncio
async def test_get_all_tasks_session_was_revoked(
    user_session_repository: UserSessionRepository,
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    moderator = await test_user_factory.create_moderator_info()

    moderator.user_session.revoke()
    await user_session_repository.update(moderator.user_session)


    response = await test_client.get(
        f'/tasks/?page=1&size=5',
        headers={
            "Authorization": f"Bearer {moderator.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )

@pytest.mark.asyncio
async def test_get_all_tasks_not_enough_rights(
    test_user_factory: UserFactory,
    test_client: AsyncClient
) -> None:
    user = await test_user_factory.create_user_info()

    response = await test_client.get(
        f'/tasks/?page=1&size=5',
        headers={
            "Authorization": f"Bearer {user.access_token}"
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation"
    )
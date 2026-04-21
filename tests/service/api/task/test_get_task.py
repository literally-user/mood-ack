from http import HTTPStatus
from uuid import uuid4

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr, IsFloat

from tests.service.factories import UserFactory, TaskFactory
from prodik.application.interfaces.repositories import UserSessionRepository
from prodik.domain.task import InputType

@pytest.mark.asyncio
async def test_get_task_ok(
    test_user_factory: UserFactory,
    test_task_factory: TaskFactory,
    test_client: AsyncClient,
) -> None:
    user = await test_user_factory.create_user_info()
    task = await test_task_factory.create_done_task(user.user, InputType.RAW)

    response = await test_client.get(
        f'/tasks/{task.id}',
        headers={
            "Authorization": f"Bearer {user.access_token}",
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == IsPartialDict(
        id=IsStr(),
        owner_id=str(user.user.id),
        state="DONE",
        input_type="RAW",
        input_id=IsStr(),
        result=IsFloat(),
        created_at=IsStr(),
        updated_at=IsStr(),
    )

@pytest.mark.asyncio
async def test_get_task_session_was_revoked(
    user_session_repository: UserSessionRepository,
    test_user_factory: UserFactory,
    test_task_factory: TaskFactory,
    test_client: AsyncClient,
) -> None:
    user = await test_user_factory.create_user_info()
    task = await test_task_factory.create_done_task(user.user, InputType.RAW)

    user.user_session.revoke()
    await user_session_repository.update(user.user_session)

    response = await test_client.get(
        f'/tasks/{task.id}',
        headers={
            "Authorization": f"Bearer {user.access_token}",
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )


@pytest.mark.asyncio
async def test_get_task_not_found(
    test_user_factory: UserFactory,
    test_client: AsyncClient,
) -> None:
    user = await test_user_factory.create_user_info()

    response = await test_client.get(
        f'/tasks/{uuid4()}',
        headers={
            "Authorization": f"Bearer {user.access_token}",
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="Task not found"
    )

@pytest.mark.asyncio
async def test_get_task_not_enough_rights(
    test_user_factory: UserFactory,
    test_task_factory: TaskFactory,
    test_client: AsyncClient,
) -> None:
    first_user = await test_user_factory.create_user_info()
    second_user = await test_user_factory.create_user_info()

    second_task = await test_task_factory.create_done_task(second_user.user, InputType.RAW)

    response = await test_client.get(
        f'/tasks/{second_task.id}',
        headers={
            "Authorization": f"Bearer {first_user.access_token}",
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation"
    )
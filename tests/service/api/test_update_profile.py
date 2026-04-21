from http import HTTPStatus

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict
from uuid import uuid4

from prodik.application.interfaces.repositories import UserSessionRepository

from tests.service.factories import (
    UpdateProfileRequestFactory,
    UserFactory,
    gen_string,
)


@pytest.mark.asyncio
async def test_update_profile_ok(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build()

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_profile_user_not_found(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build()

    response = await test_client.put(
        f"/users/{uuid4()}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == IsPartialDict(
        detail="User not found"
    )


@pytest.mark.asyncio
async def test_update_profile_session_revoked(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
    user_session_repository: UserSessionRepository,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    test_moderator.user_session.revoke()
    await user_session_repository.update(test_moderator.user_session)

    request = UpdateProfileRequestFactory.build()

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )


@pytest.mark.asyncio
async def test_update_profile_forbidden(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build()

    response = await test_client.put(
        f"/users/{test_moderator.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation"
    )


@pytest.mark.asyncio
async def test_update_profile_email_invalid(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        email="invalid-email@@"
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Email invalid format",
        meta=IsPartialDict(
            field="email",
            value=request['email'],
        )
    )


@pytest.mark.asyncio
async def test_update_profile_username_invalid(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        username="romagay@"
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_profile_username_too_short(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        username=gen_string(3, 4)
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_profile_username_too_long(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        username=gen_string(31, 31)
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_profile_first_name_too_short(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        first_name=""
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_profile_first_name_too_long(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        first_name=gen_string(31, 31)
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_profile_last_name_too_short(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        last_name=""
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_profile_last_name_too_long(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        last_name=gen_string(31, 31)
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_profile_age_too_small(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        age=17
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_profile_age_too_big(
    test_client: AsyncClient,
    test_user_factory: UserFactory,
) -> None:
    test_user = await test_user_factory.create_user_info()
    test_moderator = await test_user_factory.create_moderator_info()
    request = UpdateProfileRequestFactory.build(
        age=100
    )

    response = await test_client.put(
        f"/users/{test_user.user.id}/profile",
        json=request,
        headers={"Authorization": f"Bearer {test_moderator.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
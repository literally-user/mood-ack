from http import HTTPStatus
import random

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict

from tests.service.factories import UpdateProfileRequestFactory, gen_string, TestUserInformation

@pytest.mark.asyncio
async def test_update_current_profile_ok(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build()

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_current_profile_email_invalid(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        email="invalid-email@@"
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Email invalid format",
        meta=IsPartialDict(
            field="email",
            value=request.email,
        )
    )

@pytest.mark.asyncio
async def test_update_current_profile_username_invalid(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        username="romagay@"
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Username cannot start with number and contain special characters",
        meta=IsPartialDict(
            field="username",
            value=request.username,
        )
    )


@pytest.mark.asyncio
async def test_update_current_profile_username_too_short(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        username=gen_string(3, 4)
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Username cannot be shorter than 5 symbols",
        meta=IsPartialDict(
            field="username",
            value=request.username,
        )
    )


@pytest.mark.asyncio
async def test_update_current_profile_username_too_long(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        username=gen_string(31, 31)
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Username cannot be longer than 30 symbols",
        meta=IsPartialDict(
            field="username",
            value=request.username,
        )
    )


@pytest.mark.asyncio
async def test_update_current_profile_first_name_too_short(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        first_name=""
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_current_profile_first_name_too_long(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        first_name=gen_string(31, 31)
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_current_profile_last_name_too_short(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        last_name=""
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_current_profile_last_name_too_long(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        last_name=gen_string(31, 31)
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_current_profile_age_too_small(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        age=17
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Age cannot be smaller than 18",
        meta=IsPartialDict(
            field="age",
            value=request.age,
        )
    )

@pytest.mark.asyncio
async def test_update_current_profile_age_too_big(
    test_client: AsyncClient,
    test_user: TestUserInformation
) -> None:
    request = UpdateProfileRequestFactory.build(
        age=random.randint(99, 130)
    )

    response = await test_client.put(
        "/users/me/profile",
        json=request.model_dump(),
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Age cannot be bigger than 99",
        meta=IsPartialDict(
            field="age",
            value=request.age,
        )
    )
from http import HTTPStatus
import random

import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr

from tests.service.factories import RegisterRequestFactory, gen_string

@pytest.mark.asyncio
async def test_register_ok(test_client: AsyncClient) -> None:
    request = RegisterRequestFactory.build()
    response = await test_client.post(
        "/auth/register",
        json=request.model_dump()
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=3600,
    )

@pytest.mark.asyncio
async def test_register_username_too_short(test_client: AsyncClient) -> None:
    request = RegisterRequestFactory.build(username=gen_string(0, 4))
    response = await test_client.post(
        "/auth/register",
        json=request.model_dump()
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
async def test_register_username_too_long(test_client: AsyncClient) -> None:
    request = RegisterRequestFactory.build(username=gen_string(31, 100))
    response = await test_client.post(
        "/auth/register",
        json=request.model_dump(),
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
async def test_register_first_name_too_short(
    test_client: AsyncClient,
) -> None:
    request = RegisterRequestFactory.build(first_name="")
    response = await test_client.post(
        "/auth/register",
        json=request.model_dump()
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="First name cannot be shorter than 1 symbols",
        meta=IsPartialDict(
            field="first_name",
            value=request.first_name,
        )
    )

@pytest.mark.asyncio
async def test_register_first_name_too_long(
    test_client: AsyncClient,
) -> None:
    request = RegisterRequestFactory.build(first_name=gen_string(31,100))
    response = await test_client.post(
        "/auth/register",
        json=request.model_dump()
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="First name cannot be longer than 30 symbols",
        meta=IsPartialDict(
            field="first_name",
            value=request.first_name,
        )
    )

@pytest.mark.asyncio
async def test_register_last_name_too_short(
    test_client: AsyncClient,
) -> None:
    request = RegisterRequestFactory.build(last_name="")
    response = await test_client.post(
        "/auth/register",
        json=request.model_dump()
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Last name cannot be shorter than 1 symbols",
        meta=IsPartialDict(
            field="last_name",
            value=request.last_name,
        )
    )

@pytest.mark.asyncio
async def test_register_last_name_too_long(test_client: AsyncClient) -> None:
    request = RegisterRequestFactory.build(
        last_name=gen_string(31, 100)
    )

    response = await test_client.post(
        "/auth/register",
        json=request.model_dump()
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Last name cannot be longer than 30 symbols",
        meta=IsPartialDict(
            field="last_name",
            value=request.last_name,
        )
    )

@pytest.mark.asyncio
async def test_register_age_too_small(test_client: AsyncClient) -> None:
    request = RegisterRequestFactory.build(age=random.randint(0, 17))

    response = await test_client.post(
        "/auth/register",
        json=request.model_dump()
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
async def test_register_age_too_big(test_client: AsyncClient) -> None:
    request = RegisterRequestFactory.build(age=random.randint(100, 130))

    response = await test_client.post(
        "/auth/register",
        json=request.model_dump()
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail="Age cannot be bigger than 99",
        meta=IsPartialDict(
            field="age",
            value=request.age,
        )
    )

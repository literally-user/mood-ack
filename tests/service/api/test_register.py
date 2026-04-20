from http import HTTPStatus
import random

import pytest
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "username",
        "first_name",
        "last_name",
        "email",
        "password",
        "age"
    ), [
        ("literally", "literally", "ltu", "contact@literally.io", "SuperSecretPassword123", 18),
        ("Donhua", "Don", "Hua", "huanitolecehuano@gond.onio", "ILoveMiskaRis", 32),
        ("oiiisk", "rubby", "ltexam", "f@ff.io", "iDs3dfisiii123132", 87),
    ]
)
async def test_register_ok(
    username: str,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    age: int,
    test_client: AsyncClient
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "age": age
        }
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        refresh_token=IsStr(),
        expires_in=3600,
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "username",
        "exception_text"
    ), [
        ("", "Username cannot be shorter than 5 symbols"),
        ("a", "Username cannot be shorter than 5 symbols"),
        ("ab", "Username cannot be shorter than 5 symbols"),
        ("abc", "Username cannot be shorter than 5 symbols"),
        ("abcd", "Username cannot be shorter than 5 symbols"),
    ]
)
async def test_register_username_too_short(
    faker: Faker,
    username: str,
    exception_text: str,
    test_client: AsyncClient,
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": username,
            "first_name": faker.name(),
            "last_name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "age": random.randint(18, 88)
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="username",
            value=username,
        )
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "username",
        "exception_text"
    ), [
        ("x"*31, "Username cannot be longer than 30 symbols"),
        ("x"*32, "Username cannot be longer than 30 symbols"),
        ("x"*33, "Username cannot be longer than 30 symbols"),
        ("x"*34, "Username cannot be longer than 30 symbols"),
    ]
)
async def test_register_username_too_long(
    faker: Faker,
    username: str,
    exception_text: str,
    test_client: AsyncClient,
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": username,
            "first_name": faker.name(),
            "last_name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "age": random.randint(18, 88)
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="username",
            value=username,
        )
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "firstname",
        "exception_text"
    ), [
        ("", "First name cannot be shorter than 1 symbols"),
    ]
)
async def test_register_first_name_too_short(
    faker: Faker,
    firstname: str,
    exception_text: str,
    test_client: AsyncClient,
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": faker.user_name(),
            "first_name": firstname,
            "last_name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "age": random.randint(18, 88)
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="first_name",
            value=firstname,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "firstname",
        "exception_text"
    ), [
        ("x"*31, "First name cannot be longer than 30 symbols"),
        ("x"*32, "First name cannot be longer than 30 symbols"),
        ("x"*33, "First name cannot be longer than 30 symbols"),
        ("x"*34, "First name cannot be longer than 30 symbols"),
    ]
)
async def test_register_first_name_too_long(
    faker: Faker,
    firstname: str,
    exception_text: str,
    test_client: AsyncClient,
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": faker.user_name(),
            "first_name": firstname,
            "last_name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "age": random.randint(18, 88)
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="first_name",
            value=firstname,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "lastname",
        "exception_text"
    ), [
        ("", "Last name cannot be shorter than 1 symbols"),
    ]
)
async def test_register_last_name_too_short(
    faker: Faker,
    lastname: str,
    exception_text: str,
    test_client: AsyncClient,
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": faker.user_name(),
            "first_name": faker.name(),
            "last_name": lastname,
            "email": faker.email(),
            "password": faker.password(),
            "age": random.randint(18, 88)
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="last_name",
            value=lastname,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "lastname",
        "exception_text"
    ), [
        ("x"*31, "Last name cannot be longer than 30 symbols"),
        ("x"*32, "Last name cannot be longer than 30 symbols"),
        ("x"*33, "Last name cannot be longer than 30 symbols"),
        ("x"*34, "Last name cannot be longer than 30 symbols"),
    ]
)
async def test_register_last_name_too_long(
    faker: Faker,
    lastname: str,
    exception_text: str,
    test_client: AsyncClient,
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": faker.user_name(),
            "first_name": faker.name(),
            "last_name": lastname,
            "email": faker.email(),
            "password": faker.password(),
            "age": random.randint(18, 88)
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="last_name",
            value=lastname,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "age",
        "exception_text"
    ), [
        (17, "Age cannot be smaller than 18"),
        (16, "Age cannot be smaller than 18"),
        (15, "Age cannot be smaller than 18")
    ]
)
async def test_register_age_too_small(
    faker: Faker,
    age: int,
    exception_text: str,
    test_client: AsyncClient
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": faker.user_name(),
            "first_name": faker.name(),
            "last_name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "age": age,
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="age",
            value=age,
        )
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "age",
        "exception_text"
    ), [
        (100, "Age cannot be bigger than 99"),
        (101, "Age cannot be bigger than 99"),
        (102, "Age cannot be bigger than 99")
    ]
)
async def test_register_age_too_big(
    faker: Faker,
    age: int,
    exception_text: str,
    test_client: AsyncClient
) -> None:
    response = await test_client.post(
        "/auth/register",
        json={
            "username": faker.user_name(),
            "first_name": faker.name(),
            "last_name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "age": age,
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="age",
            value=age,
        )
    )

import pytest
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict
import random

from tests.service.factories import TestUserInformation

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "username",
        "first_name",
        "last_name",
        "email",
        "age"
    ), [
        ("literally", "literally", "ltu", "contact@literally.io", 18),
        ("Donhua", "Don", "Hua", "huanitolecehuano@gond.onio", 32),
        ("oiiisk", "rubby", "ltexam", "f@ff.io", 87),
    ]
)
async def test_update_current_profile_ok(
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    age: int,

    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "age": age,
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 204

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "email",
        "exception_text",
    ), [
        ("bibibob!@jsdjfjj", "Email invalid format"),
        ("romagay@ioooo,..ciu", "Email invalid format"),
        ("@hotmail.com", "Email invalid format")
    ]
)
async def test_update_current_profile_email_invalid_format(
    email: str,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "email": email,
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": faker.user_name(),
            "age": random.randint(18, 88),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="email",
            value=email,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "username",
        "exception_text",
    ), [
        ("ooooooooooo!!", "Username cannot start with number and contain special characters"),
        ("romagay@", "Username cannot start with number and contain special characters"),
        ("Hettte_keru12", "Username cannot start with number and contain special characters")
    ]
)
async def test_update_current_profile_username_invalid_format(
    username: str,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": username,
            "age": random.randint(18, 88),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
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
        "exception_text",
    ), [
        ("li", "Username cannot be shorter than 5 symbols"),
        ("puk", "Username cannot be shorter than 5 symbols"),
        ("peru", "Username cannot be shorter than 5 symbols")
    ]
)
async def test_update_current_profile_username_too_short(
    username: str,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": username,
            "age": random.randint(18, 88),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
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
        "exception_text",
    ), [
        ("x"*31, "Username cannot be longer than 30 symbols"),
        ("x"*32, "Username cannot be longer than 30 symbols"),
        ("x"*33, "Username cannot be longer than 30 symbols")
    ]
)
async def test_update_current_profile_username_too_long(
    username: str,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": username,
            "age": random.randint(18, 88),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
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
        "first_name",
        "exception_text",
    ), [
        ("", "First name cannot be shorter than 1 symbols"),
    ]
)
async def test_update_current_profile_first_name_too_short(
    first_name: str,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "first_name": first_name,
            "last_name": faker.first_name(),
            "username": faker.user_name(),
            "email": faker.email(),
            "age": random.randint(18, 88),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="first_name",
            value=first_name,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "first_name",
        "exception_text",
    ), [
        ("x"*31, "First name cannot be longer than 30 symbols"),
        ("x"*32, "First name cannot be longer than 30 symbols"),
        ("x"*33, "First name cannot be longer than 30 symbols")
    ]
)
async def test_update_current_profile_first_name_too_long(
    first_name: str,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "email": faker.email(),
            "first_name": first_name,
            "last_name": faker.last_name(),
            "username": faker.user_name(),
            "age": random.randint(18, 88),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="first_name",
            value=first_name,
        )
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "last_name",
        "exception_text",
    ), [
        ("", "Last name cannot be shorter than 1 symbols"),
    ]
)
async def test_update_current_profile_last_name_too_short(
    last_name: str,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "first_name": faker.first_name(),
            "last_name": last_name,
            "username": faker.user_name(),
            "email": faker.email(),
            "age": random.randint(18, 88),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="last_name",
            value=last_name,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "last_name",
        "exception_text",
    ), [
        ("x"*31, "Last name cannot be longer than 30 symbols"),
        ("x"*32, "Last name cannot be longer than 30 symbols"),
        ("x"*33, "Last name cannot be longer than 30 symbols")
    ]
)
async def test_update_current_profile_last_name_too_long(
    last_name: str,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "email": faker.email(),
            "last_name": last_name,
            "first_name": faker.first_name(),
            "username": faker.user_name(),
            "age": random.randint(18, 88),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="last_name",
            value=last_name,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "age",
        "exception_text",
    ), [
        (17, "Age cannot be smaller than 18"),
        (16, "Age cannot be smaller than 18"),
        (15, "Age cannot be smaller than 18"),
    ]
)
async def test_update_current_profile_age_too_small(
    age: int,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": faker.user_name(),
            "email": faker.email(),
            "age": age,
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
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
        "exception_text",
    ), [
        (100, "Age cannot be bigger than 99"),
        (101, "Age cannot be bigger than 99"),
        (102, "Age cannot be bigger than 99"),
    ]
)
async def test_update_current_profile_age_too_big(
    age: int,
    exception_text: str,

    faker: Faker,
    test_client: AsyncClient,
    test_user_info: TestUserInformation
) -> None:
    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": test_user_info.user.email.value,
            "password": test_user_info.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        "/users/me/profile",
        json={
            "email": faker.email(),
            "last_name": faker.last_name(),
            "first_name": faker.first_name(),
            "username": faker.user_name(),
            "age": age,
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        detail=exception_text,
        meta=IsPartialDict(
            field="age",
            value=age,
        )
    )
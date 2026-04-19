import pytest
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict
from dishka import AsyncContainer
from uuid import uuid4

from prodik.application.interfaces.repositories import UserRepository, UserSessionRepository

from tests.service.factories import create_user_info

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
async def test_update_profile_ok(
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    age: int,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)
    
    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
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
        "username",
        "first_name",
        "last_name",
        "email",
        "age"
    ), [
        ("literally", "literally", "ltu", "contact@literally.io", 18),
    ]
)
async def test_update_profile_user_not_found(
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    age: int,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)
    
    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{uuid4()}/profile",
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

    assert response.status_code == 404
    assert response.json() == IsPartialDict(
        detail="User not found"
    )

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
    ]
)
async def test_update_profile_session_revoked(
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    age: int,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_session_repository = await container.get(UserSessionRepository)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    moderator.user_session.revoke()
    await user_session_repository.update(moderator.user_session)

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
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

    assert response.status_code == 403
    assert response.json() == IsPartialDict(
        detail="Session was revoked"
    )

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
    ]
)
async def test_update_profile_forbidden(
    email: str,
    username: str,
    first_name: str,
    last_name: str,
    age: int,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
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

    assert response.status_code == 403
    assert response.json() == IsPartialDict(
        detail="Not enough rights to perform operation"
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("email", "exception_text"),
    [
        ("bibibob!@jsdjfjj", "Email invalid format"),
        ("romagay@ioooo,..ciu", "Email invalid format"),
        ("@hotmail.com", "Email invalid format"),
    ]
)
async def test_update_profile_email_invalid_format(
    email: str,
    exception_text: str,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": email,
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": faker.user_name(),
            "age": faker.random_int(18, 90),
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
    ("username", "exception_text"),
    [
        ("ooooooooooo!!", "Username cannot start with number and contain special characters"),
        ("romagay@", "Username cannot start with number and contain special characters"),
        ("Hettte_keru12", "Username cannot start with number and contain special characters"),
    ]
)
async def test_update_profile_username_invalid_format(
    username: str,
    exception_text: str,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": username,
            "age": faker.random_int(18, 90),
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
    ("username", "exception_text"),
    [
        ("li", "Username cannot be shorter than 5 symbols"),
        ("puk", "Username cannot be shorter than 5 symbols"),
        ("peru", "Username cannot be shorter than 5 symbols"),
    ]
)
async def test_update_profile_username_too_short(
    username: str,
    exception_text: str,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": username,
            "age": faker.random_int(18, 90),
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
    ("username", "exception_text"),
    [
        ("x" * 31, "Username cannot be longer than 30 symbols"),
        ("x" * 32, "Username cannot be longer than 30 symbols"),
        ("x" * 33, "Username cannot be longer than 30 symbols"),
    ]
)
async def test_update_profile_username_too_long(
    username: str,
    exception_text: str,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "username": username,
            "age": faker.random_int(18, 90),
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
async def test_update_profile_first_name_too_short(
    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    first_name = ""

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": first_name,
            "last_name": faker.last_name(),
            "username": faker.user_name(),
            "age": faker.random_int(18, 90),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        detail="First name cannot be shorter than 1 symbols",
        meta=IsPartialDict(
            field="first_name",
            value=first_name,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("first_name", "exception_text"),
    [
        ("x" * 31, "First name cannot be longer than 30 symbols"),
        ("x" * 32, "First name cannot be longer than 30 symbols"),
        ("x" * 33, "First name cannot be longer than 30 symbols"),
    ]
)
async def test_update_profile_first_name_too_long(
    first_name: str,
    exception_text: str,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": first_name,
            "last_name": faker.last_name(),
            "username": faker.user_name(),
            "age": faker.random_int(18, 90),
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
async def test_update_profile_last_name_too_short(
    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    last_name = ""

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": last_name,
            "username": faker.user_name(),
            "age": faker.random_int(18, 90),
        },
        headers={
            "Authorization": f"Bearer {auth_content['access_token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        detail="Last name cannot be shorter than 1 symbols",
        meta=IsPartialDict(
            field="last_name",
            value=last_name,
        )
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("last_name", "exception_text"),
    [
        ("x" * 31, "Last name cannot be longer than 30 symbols"),
        ("x" * 32, "Last name cannot be longer than 30 symbols"),
        ("x" * 33, "Last name cannot be longer than 30 symbols"),
    ]
)
async def test_update_profile_last_name_too_long(
    last_name: str,
    exception_text: str,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": last_name,
            "username": faker.user_name(),
            "age": faker.random_int(18, 90),
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
    ("age", "exception_text"),
    [
        (17, "Age cannot be smaller than 18"),
        (16, "Age cannot be smaller than 18"),
        (15, "Age cannot be smaller than 18"),
    ]
)
async def test_update_profile_age_too_small(
    age: int,
    exception_text: str,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
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

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("age", "exception_text"),
    [
        (100, "Age cannot be bigger than 99"),
        (101, "Age cannot be bigger than 99"),
        (102, "Age cannot be bigger than 99"),
    ]
)
async def test_update_profile_age_too_big(
    age: int,
    exception_text: str,

    faker: Faker,
    test_container: AsyncContainer,
    test_client: AsyncClient,
) -> None:
    moderator = await create_user_info(faker, test_container)
    target = await create_user_info(faker, test_container)

    async with test_container() as container:
        user_repository = await container.get(UserRepository)

    moderator.user.promote()
    await user_repository.update(moderator.user)

    auth_response = await test_client.post(
        "/auth/login",
        json={
            "email": moderator.user.email.value,
            "password": moderator.password,
        }
    )

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/users/{target.user.id}/profile",
        json={
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
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
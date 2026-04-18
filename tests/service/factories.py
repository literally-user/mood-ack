from dataclasses import dataclass
from uuid import uuid4
import random

import pytest
from faker import Faker
from dishka import AsyncContainer

from prodik.domain.user import User, UserId
from prodik.domain.credentials import UserSession, LocalAuthorization, UserSessionId, LocalAuthorizationId
from prodik.application.interfaces.token_manager import RefreshTokenManager, AccessTokenManager
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import UserRepository, UserSessionRepository, LocalAuthorizationRepository
from prodik.infrastructure.config import APIConfig

@dataclass
class TestUserInformation:
    user: User
    user_session: UserSession
    local_authorization: LocalAuthorization

    password: str
    access_token: str

async def create_user_info(faker: Faker, test_container: AsyncContainer) -> TestUserInformation:
    async with test_container() as container:
        refresh_token_manager = await container.get(RefreshTokenManager)
        access_token_manager = await container.get(AccessTokenManager)
        password_hasher = await container.get(PasswordHasher)

        local_authorization_repository = await container.get(LocalAuthorizationRepository)
        user_session_repository = await container.get(UserSessionRepository)
        user_repository = await container.get(UserRepository)

        config = await container.get(APIConfig)

    user = User.new(
        id=UserId(uuid4()),
        username=faker.user_name(),
        first_name=faker.name(),
        last_name=faker.name(),
        email=faker.email(),
        age=random.randint(18, 98),
    )

    password = faker.password()
    hashed_password = password_hasher.hash(password)
    refresh_token = refresh_token_manager.generate()
    access_token = access_token_manager.generate(
        user,
        expires_in=config.expires_in
    )
    user_session = UserSession.new(
        id=UserSessionId(uuid4()),
        user=user,
        ip=faker.ipv4(),
        refresh_token=refresh_token
    )
    local_authorization = LocalAuthorization.new(
        id=LocalAuthorizationId(uuid4()),
        user=user,
        password=hashed_password
    )

    await user_repository.create(user)
    await user_session_repository.create(user_session)
    await local_authorization_repository.create(local_authorization)

    return TestUserInformation(
        user=user,
        user_session=user_session,
        local_authorization=local_authorization,
        password=password,
        access_token=access_token,
    )
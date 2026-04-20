from string import ascii_letters
from dataclasses import dataclass
from uuid import uuid4
import random

from faker import Faker
from dishka import AsyncContainer
from pydantic import BaseModel, EmailStr
from polyfactory.factories.pydantic_factory import ModelFactory

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

class RegisterRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str
    email: EmailStr
    age: int

class UpdateProfileRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    age: int

class UpdateProfileRequestFactory(ModelFactory[UpdateProfileRequest]):
    __model__ = UpdateProfileRequest

    @classmethod
    def age(cls) -> int:
        return random.randint(18, 98)

    @classmethod
    def email(cls) -> str:
        return gen_string(5, 10) + "@example.com"

class RegisterRequestFactory(ModelFactory[RegisterRequest]):
    __model__ = RegisterRequest

    @classmethod
    def age(cls) -> int:
        return random.randint(18, 98)

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
        ip="127.0.0.1",
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

def gen_string(a: int, b: int) -> str:
    return ''.join(random.choice(list(ascii_letters)) for _ in range(random.randint(a, b)))
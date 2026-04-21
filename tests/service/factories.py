from typing import TypedDict
from string import ascii_letters
from dataclasses import dataclass
from uuid import uuid4
import random

from faker import Faker
from dishka import AsyncContainer
from polyfactory.factories import TypedDictFactory

from prodik.domain.user import User, UserId, Username, Age, FirstName, LastName, Email
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

class RegisterRequest(TypedDict):
    username: str
    first_name: str
    last_name: str
    password: str
    email: str
    age: int

class UpdateProfileRequest(TypedDict):
    username: str
    first_name: str
    last_name: str
    email: str
    age: int

class UpdateProfileRequestFactory(TypedDictFactory[UpdateProfileRequest]):
    @classmethod
    def age(cls) -> int:
        return random.randint(18, 98)

    @classmethod
    def email(cls) -> str:
        return gen_string(5, 10) + "@example.com"

class RegisterRequestFactory(TypedDictFactory[RegisterRequest]):
    @classmethod
    def age(cls) -> int:
        return random.randint(18, 98)

    @classmethod
    def email(cls) -> str:
        return gen_string(5, 10) + "@example.com"

@dataclass
class UserFactory:
    faker: Faker
    user_repository: UserRepository
    refresh_token_manager: RefreshTokenManager
    access_token_manager: AccessTokenManager
    user_session_repository: UserSessionRepository
    local_authorization_repository: LocalAuthorizationRepository
    password_hasher: PasswordHasher
    config: APIConfig

    async def create_user_info(self) -> TestUserInformation:
        user = User.new(
            id=UserId(uuid4()),
            username=self.faker.user_name(),
            first_name=self.faker.name(),
            last_name=self.faker.name(),
            email=self.faker.email(),
            age=random.randint(18, 98),
        )

        password = self.faker.password()
        hashed_password = self.password_hasher.hash(password)
        refresh_token = self.refresh_token_manager.generate()
        access_token = self.access_token_manager.generate(
            user,
            expires_in=self.config.expires_in
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

        await self.user_repository.create(user)
        await self.user_session_repository.create(user_session)
        await self.local_authorization_repository.create(local_authorization)

        return TestUserInformation(
            user=user,
            user_session=user_session,
            local_authorization=local_authorization,
            password=password,
            access_token=access_token,
        )

    async def create_moderator_info(self) -> TestUserInformation:
        information = await self.create_user_info()
        information.user.promote()
        await self.user_repository.update(information.user)
        return information

def gen_string(a: int, b: int) -> str:
    return ''.join(random.choice(list(ascii_letters)) for _ in range(random.randint(a, b)))
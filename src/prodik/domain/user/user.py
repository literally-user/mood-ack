import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, NewType
from uuid import UUID

from prodik.domain.shared import Entity, ValueObject
from prodik.domain.user import UserRole, UserStatus
from prodik.domain.user.errors import (
    AgeTooBigError,
    AgeTooSmallError,
    EmailInvalidFormatError,
    InvalidUsernameFormatError,
    UsernameTooLongError,
    UsernameTooShortError,
)

MAX_USERNAME_LENGTH: Final[int] = 30
MIN_USERNAME_LENGTH: Final[int] = 5

MAX_FIRST_NAME_LENGTH: Final[int] = 30
MIN_FIRST_NAME_LENGTH: Final[int] = 1

MAX_SECOND_NAME_LENGTH: Final[int] = 30
MIN_SECOND_NAME_LENGTH: Final[int] = 1

MIN_ALLOWED_AGE: Final[int] = 18
MAX_ALLOWED_AGE: Final[int] = 99


UserId = NewType("UserId", UUID)


class Email(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise EmailInvalidFormatError(
                "Email invalid format", metadata={"field": "email", "value": value}
            )

        super().__init__(value)


class Username(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) > MAX_USERNAME_LENGTH:
            raise UsernameTooLongError(
                f"Username cannot be longer than {MAX_USERNAME_LENGTH} symbols",
                metadata={"field": "username", "value": value},
            )
        if len(value) < MIN_USERNAME_LENGTH:
            raise UsernameTooLongError(
                f"Username cannot be shorter than {MIN_USERNAME_LENGTH} symbols",
                metadata={"field": "username", "value": value},
            )

        if not re.match(r"^[A-Za-z][A-Za-z]*$", value):
            raise InvalidUsernameFormatError(
                "Username cannot start with number and contain special characters",
                metadata={"field": "username", "value": value},
            )

        super().__init__(value)


class FirstName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) > MAX_FIRST_NAME_LENGTH:
            raise UsernameTooLongError(
                f"First name cannot be longer than {MAX_FIRST_NAME_LENGTH} symbols",
                metadata={"field": "first_name", "value": value},
            )
        if len(value) < MIN_FIRST_NAME_LENGTH:
            raise UsernameTooShortError(
                f"First name cannot be shorter than {MIN_FIRST_NAME_LENGTH} symbols",
                metadata={"field": "first_name", "value": value},
            )
        super().__init__(value)


class SecondName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) > MAX_SECOND_NAME_LENGTH:
            raise UsernameTooLongError(
                f"Second name cannot be longer than {MAX_SECOND_NAME_LENGTH} symbols",
                metadata={"field": "second_name", "value": value},
            )
        if len(value) < MIN_SECOND_NAME_LENGTH:
            raise UsernameTooShortError(
                f"Second name cannot be shorter than {MIN_SECOND_NAME_LENGTH} symbols",
                metadata={"field": "second_name", "value": value},
            )
        super().__init__(value)


class Age(ValueObject[int]):
    def __init__(self, value: int) -> None:
        if value > MAX_ALLOWED_AGE:
            raise AgeTooBigError(
                f"Age cannot be bigger than {MAX_ALLOWED_AGE}",
                metadata={"field": "age", "value": value},
            )
        if value < MIN_ALLOWED_AGE:
            raise AgeTooSmallError(
                f"Age cannot be smaller than {MIN_ALLOWED_AGE}",
                metadata={"field": "age", "value": value},
            )
        super().__init__(value)


@dataclass(kw_only=True)
class User(Entity[UserId]):
    _username: Username
    _first_name: FirstName
    _last_name: SecondName
    _email: Email
    _age: Age
    _role: UserRole
    _status: UserStatus

    @classmethod
    def new(
        cls,
        id: UserId,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        age: int,
    ) -> "User":
        now = datetime.now(tz=UTC)
        return User(
            _id=id,
            _username=Username(username),
            _first_name=FirstName(first_name),
            _last_name=SecondName(last_name),
            _email=Email(email),
            _age=Age(age),
            _role=UserRole.USER,
            _status=UserStatus.ACTIVE,
            _created_at=now,
            _updated_at=now,
        )

    @property
    def email(self) -> str:
        return self._email.value

    @property
    def username(self) -> str:
        return self._username.value

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def id(self) -> UserId:
        return self._id

    def change_username(self, username: str) -> None:
        self._username = Username(username)

    def change_first_name(self, first_name: str) -> None:
        self._first_name = FirstName(first_name)

    def change_second_name(self, second_name: str) -> None:
        self.second_name = SecondName(second_name)

    def change_email(self, email: str) -> None:
        self._email = Email(email)

    def change_age(self, age: int) -> None:
        self._age = Age(age)

    def set_user_role(self) -> None:
        self._role = UserRole.USER

    def set_moderator_role(self) -> None:
        self._role = UserRole.MODERATOR

    def activate(self) -> None:
        self._status = UserStatus.ACTIVE

    def deactivate(self) -> None:
        self._status = UserStatus.DEACTIVATED

    def deactivated(self) -> bool:
        return self._status == UserStatus.DEACTIVATED

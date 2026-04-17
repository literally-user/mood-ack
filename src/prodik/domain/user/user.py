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
    FirstNameTooLongError,
    FirstNameTooShortError,
    InvalidUsernameFormatError,
    SecondNameTooLongError,
    SecondNameTooShortError,
    UsernameTooLongError,
    UsernameTooShortError,
)

MAX_USERNAME_LENGTH: Final[int] = 30
MIN_USERNAME_LENGTH: Final[int] = 5

MAX_FIRST_NAME_LENGTH: Final[int] = 30
MIN_FIRST_NAME_LENGTH: Final[int] = 1

MAX_LAST_NAME_LENGTH: Final[int] = 30
MIN_LAST_NAME_LENGTH: Final[int] = 1

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
            raise UsernameTooShortError(
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
            raise FirstNameTooLongError(
                f"First name cannot be longer than {MAX_FIRST_NAME_LENGTH} symbols",
                metadata={"field": "first_name", "value": value},
            )
        if len(value) < MIN_FIRST_NAME_LENGTH:
            raise FirstNameTooShortError(
                f"First name cannot be shorter than {MIN_FIRST_NAME_LENGTH} symbols",
                metadata={"field": "first_name", "value": value},
            )
        super().__init__(value)


class LastName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) > MAX_LAST_NAME_LENGTH:
            raise SecondNameTooLongError(
                f"Last name cannot be longer than {MAX_LAST_NAME_LENGTH} symbols",
                metadata={"field": "last_name", "value": value},
            )
        if len(value) < MIN_LAST_NAME_LENGTH:
            raise SecondNameTooShortError(
                f"Last name cannot be shorter than {MIN_LAST_NAME_LENGTH} symbols",
                metadata={"field": "last_name", "value": value},
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
    username: Username
    first_name: FirstName
    last_name: LastName
    email: Email
    age: Age
    role: UserRole
    status: UserStatus

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
            id=id,
            username=Username(username),
            first_name=FirstName(first_name),
            last_name=LastName(last_name),
            email=Email(email),
            age=Age(age),
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )

    def change_username(self, username: str) -> None:
        self._username = Username(username)
        self.touch()

    def change_first_name(self, first_name: str) -> None:
        self._first_name = FirstName(first_name)
        self.touch()

    def change_last_name(self, last_name: str) -> None:
        self._last_name = LastName(last_name)
        self.touch()

    def change_email(self, email: str) -> None:
        self._email = Email(email)
        self.touch()

    def change_age(self, age: int) -> None:
        self._age = Age(age)
        self.touch()

    def set_user_role(self) -> None:
        self._role = UserRole.USER
        self.touch()

    def set_moderator_role(self) -> None:
        self._role = UserRole.MODERATOR
        self.touch()

    def activate(self) -> None:
        self._status = UserStatus.ACTIVE
        self.touch()

    def deactivate(self) -> None:
        self._status = UserStatus.DEACTIVATED
        self.touch()

    def is_deactivated(self) -> bool:
        return self._status == UserStatus.DEACTIVATED

    def can_manage_users(self) -> bool:
        return self._role == UserRole.MODERATOR

    def can_manage_tasks(self) -> bool:
        return self._role == UserRole.MODERATOR

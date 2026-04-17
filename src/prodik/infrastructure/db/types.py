from typing import Any, override

from sqlalchemy import Dialect, Integer, String
from sqlalchemy.types import TypeDecorator

from prodik.domain.credentials import IP
from prodik.domain.user import (
    Age,
    Email,
    FirstName,
    LastName,
    Username,
)


class UsernameType(TypeDecorator[Username]):
    impl = String
    cache_ok = True

    def process_bind_param(
        self,
        value: Username | None,
        dialect: Dialect,
    ) -> str | None:
        if value is None:
            return None

        return value.value

    def process_result_value(
        self,
        value: str | None,
        dialect: Dialect,
    ) -> Username | None:
        if value is None:
            return None

        return Username(value)


class FirstNameType(TypeDecorator[FirstName]):
    impl = String
    cache_ok = True

    @override
    def process_bind_param(self, value: FirstName | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> FirstName | None:
        if value is None:
            return None

        return FirstName(value)


class LastNameType(TypeDecorator[LastName]):
    impl = String
    cache_ok = True

    @override
    def process_bind_param(self, value: LastName | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> LastName | None:
        if value is None:
            return None

        return LastName(value)


class EmailType(TypeDecorator[Email]):
    impl = String
    cache_ok = True

    @override
    def process_bind_param(self, value: Email | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(self, value: Any | None, dialect: Dialect) -> Email | None:
        if value is None:
            return None

        return Email(value)


class AgeType(TypeDecorator[Age]):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: Age | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    def process_result_value(self, value: Any | None, dialect: Dialect) -> Age | None:
        if value is None:
            return None

        return Age(value)


class IPType(TypeDecorator[IP]):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value: IP | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    def process_result_value(self, value: Any | None, dialect: Dialect) -> IP | None:
        if value is None:
            return None

        return IP(value)

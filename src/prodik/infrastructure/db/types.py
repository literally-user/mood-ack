from typing import Any, ClassVar, override

from sqlalchemy import Dialect, Integer, String
from sqlalchemy.types import TypeDecorator

from prodik.domain.credentials import IP
from prodik.domain.shared import ValueObject
from prodik.domain.user import (
    Age,
    Email,
    FirstName,
    LastName,
    Username,
)


class BaseVOTypeDecorator[T: ValueObject[Any]](TypeDecorator[T]):
    vo_class: ClassVar[type]

    @override
    def process_bind_param(self, value: T | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(self, value: Any | None, dialect: Dialect) -> T | None:
        return self.vo_class(value) if value else None


class UsernameType(BaseVOTypeDecorator[Username]):
    impl = String
    cache_ok = True
    vo_class = Username


class FirstNameType(BaseVOTypeDecorator[FirstName]):
    impl = String
    cache_ok = True
    vo_class = FirstName


class LastNameType(BaseVOTypeDecorator[LastName]):
    impl = String
    cache_ok = True
    vo_class = LastName


class AgeType(BaseVOTypeDecorator[Age]):
    impl = Integer
    cache_ok = True
    vo_class = Age


class IPType(BaseVOTypeDecorator[IP]):
    impl = String(36)
    cache_ok = True
    vo_class = IP


class EmailType(BaseVOTypeDecorator[Email]):
    impl = String
    cache_ok = True
    vo_class = Email

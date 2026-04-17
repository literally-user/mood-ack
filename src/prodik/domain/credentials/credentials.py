import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import NewType
from uuid import UUID

from prodik.domain.credentials.errors import InvalidIPAddressFormatError
from prodik.domain.shared import Entity, ValueObject
from prodik.domain.user import User, UserId

UserSessionId = NewType("UserSessionId", UUID)
LocalAuthorizationId = NewType("LocalAuthorizationId", UUID)
OAuthAuthorizationId = NewType("OAuthAuthorizationId", UUID)


class UserSessionStatus(StrEnum):
    REVOKED = "REVOKED"
    ACTIVE = "ACTIVE"


class IP(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if not re.match(
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            value,
        ):
            raise InvalidIPAddressFormatError(
                "Invalid IP address format", metadata={"field": "ip", "value": value}
            )
        super().__init__(value)


@dataclass(kw_only=True)
class UserSession(Entity[UserSessionId]):
    _ip: IP
    _user_id: UserId
    _refresh_token: str
    _status: UserSessionStatus

    @classmethod
    def new(
        cls,
        id: UserSessionId,
        user: User,
        ip: str,
        refresh_token: str,
    ) -> "UserSession":
        now = datetime.now(tz=UTC)
        return UserSession(
            _id=id,
            _ip=IP(ip),
            _user_id=user.id,
            _refresh_token=refresh_token,
            _status=UserSessionStatus.ACTIVE,
            _created_at=now,
            _updated_at=now,
        )

    @property
    def id(self) -> UserSessionId:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def ip(self) -> str:
        return self._ip.value

    @property
    def status(self) -> UserSessionStatus:
        return self._status

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    def is_revoked(self) -> bool:
        return self._status == UserSessionStatus.REVOKED

    def enable(self) -> None:
        self._status = UserSessionStatus.ACTIVE
        self.touch()

    def update_refresh_token(self, refresh_token: str) -> None:
        self._refresh_token = refresh_token
        self.touch()

    def revoke(self) -> None:
        self._status = UserSessionStatus.REVOKED
        self.touch()


@dataclass(kw_only=True)
class LocalAuthorization(Entity[LocalAuthorizationId]):
    _user_id: UserId
    _password: str

    @classmethod
    def new(
        cls, id: LocalAuthorizationId, user: User, password: str
    ) -> "LocalAuthorization":
        now = datetime.now(tz=UTC)
        return LocalAuthorization(
            _id=id,
            _user_id=user.id,
            _password=password,
            _created_at=now,
            _updated_at=now,
        )

    @property
    def id(self) -> LocalAuthorizationId:
        return self._id

    @property
    def password(self) -> str:
        return self._password

    @property
    def user_id(self) -> UserId:
        return self._user_id

    def change_password(self, new_password: str) -> None:
        self._password = new_password
        self.touch()


@dataclass(kw_only=True)
class OAuthAuthorization(Entity[OAuthAuthorizationId]):
    _user_id: UserId

    @classmethod
    def new(cls, id: OAuthAuthorizationId, user: User) -> "OAuthAuthorization":
        now = datetime.now(tz=UTC)
        return OAuthAuthorization(
            _id=id,
            _user_id=user.id,
            _created_at=now,
            _updated_at=now,
        )

    @property
    def user_id(self) -> UserId:
        return self._user_id

import re
from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from prodik.domain.credentials.errors import InvalidIPAddressFormatError
from prodik.domain.shared import Entity, ValueObject
from prodik.domain.user import User, UserId

UserSessionId = NewType("UserSessionId", UUID)
LocalAuthorizationId = NewType("LocalAuthorizationId", UUID)
OAuthAuthorizationId = NewType("OAuthAuthorizationId", UUID)


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
    _id: UserSessionId
    _ip: IP
    _user_id: UserId
    _refresh_token: str

    @classmethod
    def new(
        cls,
        id: UserSessionId,
        user: User,
        ip: str,
        refresh_token: str,
    ) -> "UserSession":
        return UserSession(
            _id=id,
            _ip=IP(ip),
            _user_id=user.id,
            _refresh_token=refresh_token,
        )

    @property
    def ip(self) -> str:
        return self._ip.value

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    def update_refresh_token(self, refresh_token: str) -> None:
        self._refresh_token = refresh_token


@dataclass(kw_only=True)
class LocalAuthorization(Entity[LocalAuthorizationId]):
    _id: LocalAuthorizationId
    _user_id: UserId
    _password: str

    @classmethod
    def new(
        cls, id: LocalAuthorizationId, user: User, password: str
    ) -> "LocalAuthorization":
        return LocalAuthorization(
            _id=id,
            _user_id=user.id,
            _password=password,
        )

    @property
    def password(self) -> str:
        return self._password


@dataclass(kw_only=True)
class OAuthAuthorization(Entity[OAuthAuthorizationId]):
    _id: OAuthAuthorizationId
    _user_id: UserId

    @classmethod
    def new(cls, id: OAuthAuthorizationId, user: User) -> "OAuthAuthorization":
        return OAuthAuthorization(
            _id=id,
            _user_id=user.id,
        )

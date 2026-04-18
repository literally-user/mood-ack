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
    ip: IP
    user_id: UserId
    refresh_token: str
    status: UserSessionStatus

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
            id=id,
            ip=IP(ip),
            user_id=user.id,
            refresh_token=refresh_token,
            status=UserSessionStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )

    def is_revoked(self) -> bool:
        return self.status == UserSessionStatus.REVOKED

    def enable(self) -> None:
        self.status = UserSessionStatus.ACTIVE
        self.touch()

    def update_refresh_token(self, refresh_token: str) -> None:
        self.refresh_token = refresh_token
        self.touch()

    def revoke(self) -> None:
        self.status = UserSessionStatus.REVOKED
        self.touch()


@dataclass(kw_only=True)
class LocalAuthorization(Entity[LocalAuthorizationId]):
    user_id: UserId
    password: str

    @classmethod
    def new(
        cls, id: LocalAuthorizationId, user: User, password: str
    ) -> "LocalAuthorization":
        now = datetime.now(tz=UTC)
        return LocalAuthorization(
            id=id,
            user_id=user.id,
            password=password,
            created_at=now,
            updated_at=now,
        )

    def change_password(self, new_password: str) -> None:
        self.password = new_password
        self.touch()


@dataclass(kw_only=True)
class OAuthAuthorization(Entity[OAuthAuthorizationId]):
    user_id: UserId

    @classmethod
    def new(cls, id: OAuthAuthorizationId, user: User) -> "OAuthAuthorization":
        now = datetime.now(tz=UTC)
        return OAuthAuthorization(
            id=id,
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )

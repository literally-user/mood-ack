from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from prodik.domain.shared import Entity

type UserId = UUID


class UserRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


@dataclass(kw_only=True)
class User(Entity[UserId]):
    id: UserId

    username: str
    password: str

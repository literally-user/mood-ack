from enum import StrEnum


class UserRole(StrEnum):
    USER = "USER"
    MODERATOR = "MODERATOR"


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DEACTIVATED = "DEACTIVATED"

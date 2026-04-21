from datetime import datetime

from pydantic import BaseModel

from prodik.domain.user import UserId, UserRole, UserStatus


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    email: str | None
    first_name: str | None
    last_name: str | None
    age: int | None
    username: str | None


class UserSchema(BaseModel):
    id: UserId
    username: str
    first_name: str
    last_name: str
    email: str
    age: int
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class GetAllUsersRequest(BaseModel):
    page: int
    size: int

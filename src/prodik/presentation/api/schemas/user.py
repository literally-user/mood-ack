from pydantic import BaseModel


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    email: str | None
    first_name: str | None
    last_name: str | None
    age: int | None
    username: str | None

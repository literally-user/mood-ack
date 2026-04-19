from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, SecretStr


class AuthResponse(BaseModel):
    access_token: Annotated[str, Field("Session access token")]
    refresh_token: Annotated[str, Field("Session refresh token")]

    expires_in: Annotated[int, Field("Access token expire date")]


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(description="Local user email")]
    password: Annotated[SecretStr, Field(description="Local user password")]


class RegisterRequest(BaseModel):
    username: Annotated[str, Field(description="Unique username")]
    first_name: Annotated[str, Field(description="First name")]
    last_name: Annotated[str, Field(description="Last name")]
    email: Annotated[str, Field(description="Unique email")]
    password: Annotated[SecretStr, Field(description="Password")]
    age: Annotated[int, Field(description="Age")]


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class OAuthRequest(BaseModel):
    code: str
    state: str
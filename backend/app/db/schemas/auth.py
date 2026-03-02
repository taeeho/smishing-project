from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: int
    email: str
    username: str
    social_type: str


class LoginResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class UserProfileResponse(BaseModel):
    user_id: int
    email: str
    username: str
    social_type: str
    age: int | None = None
    guardian_contact: str | None = None


class UserUpdateRequest(BaseModel):
    username: str | None = None
    age: int | None = None
    guardian_contact: str | None = None

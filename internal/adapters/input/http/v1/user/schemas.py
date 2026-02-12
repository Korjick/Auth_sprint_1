from uuid import UUID

from pydantic import BaseModel, field_validator


# request

class LoginRequest(BaseModel):
    login: str

    @field_validator('login')
    def normalize_login(cls, value: str) -> str:
        return value.strip()


class UserCreateRequest(LoginRequest):
    password: str
    first_name: str
    last_name: str


class UserLoginRequest(LoginRequest):
    password: str


class UserUpdateRequest(BaseModel):
    current_password: str
    new_login: str
    new_password: str

    @field_validator("new_login")
    def normalize_new_login(cls, value: str) -> str:
        return value.strip()


class RoleAssignRequest(BaseModel):
    role_id: UUID


# responses

class UserCreateResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str


class UserDetailResponse(BaseModel):
    id: UUID
    login: str
    first_name: str
    last_name: str


class UserRoleResponse(BaseModel):
    login: str
    roles: list[str]


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenResponse(UserLoginResponse):
    ...


class SessionHistoryResponse(BaseModel):
    id: UUID
    device_fingerprint: str

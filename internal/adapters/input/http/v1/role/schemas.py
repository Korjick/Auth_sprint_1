from uuid import UUID

from pydantic import BaseModel


class RoleCreateRequest(BaseModel):
    name: str


class RoleUpdateRequest(BaseModel):
    name: str


class RoleResponse(BaseModel):
    id: UUID
    name: str

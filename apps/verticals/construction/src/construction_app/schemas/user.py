from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    role: str = "vendedor"


class UserResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    nome: str
    email: str
    role: str
    ativo: bool
    created_at: datetime

    class Config:
        from_attributes = True

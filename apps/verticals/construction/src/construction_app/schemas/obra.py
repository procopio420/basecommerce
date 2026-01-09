from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ObraCreate(BaseModel):
    cliente_id: UUID
    nome: str
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    observacoes: str | None = None


class ObraUpdate(BaseModel):
    nome: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    observacoes: str | None = None
    ativa: bool | None = None


class ObraResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    cliente_id: UUID
    nome: str
    endereco: str | None
    cidade: str | None
    estado: str | None
    observacoes: str | None
    ativa: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

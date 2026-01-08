from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ClienteCreate(BaseModel):
    tipo: str  # 'PF' ou 'PJ'
    nome: str
    documento: str  # CPF ou CNPJ
    email: EmailStr | None = None
    telefone: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None
    observacoes: str | None = None


class ClienteUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    telefone: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None
    observacoes: str | None = None


class ClienteResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    tipo: str
    nome: str
    documento: str
    email: str | None
    telefone: str | None
    endereco: str | None
    cidade: str | None
    estado: str | None
    cep: str | None
    observacoes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProdutoCreate(BaseModel):
    codigo: str | None = None
    nome: str
    descricao: str | None = None
    unidade: str  # 'UN', 'KG', 'M', 'M2', 'M3'
    preco_base: Decimal


class ProdutoUpdate(BaseModel):
    codigo: str | None = None
    nome: str | None = None
    descricao: str | None = None
    unidade: str | None = None
    preco_base: Decimal | None = None
    ativo: bool | None = None


class ProdutoResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    codigo: str | None
    nome: str
    descricao: str | None
    unidade: str
    preco_base: Decimal
    ativo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

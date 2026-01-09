from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CotacaoItemCreate(BaseModel):
    produto_id: UUID
    quantidade: Decimal
    preco_unitario: Decimal
    desconto_percentual: Decimal = Decimal("0")
    observacoes: str | None = None
    ordem: int = 0


class CotacaoItemResponse(BaseModel):
    id: UUID
    produto_id: UUID
    quantidade: Decimal
    preco_unitario: Decimal
    desconto_percentual: Decimal
    valor_total: Decimal
    observacoes: str | None
    ordem: int

    class Config:
        from_attributes = True


class CotacaoCreate(BaseModel):
    cliente_id: UUID
    obra_id: UUID | None = None
    desconto_percentual: Decimal = Decimal("0")
    observacoes: str | None = None
    validade_dias: int = 7
    itens: list[CotacaoItemCreate]


class CotacaoUpdate(BaseModel):
    obra_id: UUID | None = None
    desconto_percentual: Decimal | None = None
    observacoes: str | None = None
    validade_dias: int | None = None
    itens: list[CotacaoItemCreate] | None = None


class CotacaoResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    cliente_id: UUID
    obra_id: UUID | None
    numero: str
    status: str
    desconto_percentual: Decimal
    observacoes: str | None
    validade_dias: int
    usuario_id: UUID | None
    created_at: datetime
    updated_at: datetime
    enviada_em: datetime | None
    aprovada_em: datetime | None
    convertida_em: datetime | None
    itens: list[CotacaoItemResponse] = []

    class Config:
        from_attributes = True

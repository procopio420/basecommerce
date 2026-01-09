from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PedidoItemCreate(BaseModel):
    produto_id: UUID
    quantidade: Decimal
    preco_unitario: Decimal
    desconto_percentual: Decimal = Decimal("0")
    observacoes: str | None = None
    ordem: int = 0


class PedidoItemResponse(BaseModel):
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


class PedidoCreate(BaseModel):
    cotacao_id: UUID | None = None
    cliente_id: UUID
    obra_id: UUID | None = None
    desconto_percentual: Decimal = Decimal("0")
    observacoes: str | None = None
    itens: list[PedidoItemCreate]


class PedidoUpdate(BaseModel):
    status: str | None = None
    obra_id: UUID | None = None
    desconto_percentual: Decimal | None = None
    observacoes: str | None = None


class PedidoResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    cotacao_id: UUID | None
    cliente_id: UUID
    obra_id: UUID | None
    numero: str
    status: str
    desconto_percentual: Decimal
    observacoes: str | None
    usuario_id: UUID | None
    created_at: datetime
    updated_at: datetime
    entregue_em: datetime | None
    itens: list[PedidoItemResponse] = []

    class Config:
        from_attributes = True

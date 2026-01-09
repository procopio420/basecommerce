from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from basecore.db import Base
from construction_app.models.base import BaseModelMixin


class Cotacao(Base, BaseModelMixin):
    __tablename__ = "cotacoes"

    # FK managed by database, not SQLAlchemy (Tenant/User are in auth service)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    obra_id = Column(UUID(as_uuid=True), ForeignKey("obras.id"))
    numero = Column(String(50), nullable=False)
    status = Column(
        String(20), nullable=False, default="rascunho"
    )  # rascunho, enviada, aprovada, convertida, cancelada
    desconto_percentual = Column(Numeric(5, 2), default=0)
    observacoes = Column(Text)
    validade_dias = Column(Integer, default=7)
    # User FK managed by database (User is in auth service)
    usuario_id = Column(UUID(as_uuid=True), index=True)
    enviada_em = Column(DateTime(timezone=True))
    aprovada_em = Column(DateTime(timezone=True))
    convertida_em = Column(DateTime(timezone=True))

    cliente = relationship("Cliente")
    obra = relationship("Obra")
    itens = relationship(
        "CotacaoItem",
        back_populates="cotacao",
        cascade="all, delete-orphan",
        order_by="CotacaoItem.ordem",
    )

    __table_args__ = (
        Index("idx_cotacoes_tenant_status", "tenant_id", "status"),
        Index("idx_cotacoes_cliente", "tenant_id", "cliente_id"),
        Index("idx_cotacoes_created", "tenant_id", "created_at"),
        Index("idx_cotacoes_tenant_numero", "tenant_id", "numero", unique=True),
    )


class CotacaoItem(Base, BaseModelMixin):
    __tablename__ = "cotacao_itens"

    # FK managed by database, not SQLAlchemy (Tenant is in auth service)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    cotacao_id = Column(
        UUID(as_uuid=True), ForeignKey("cotacoes.id", ondelete="CASCADE"), nullable=False
    )
    produto_id = Column(UUID(as_uuid=True), ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    desconto_percentual = Column(Numeric(5, 2), default=0)
    valor_total = Column(Numeric(10, 2), nullable=False)
    observacoes = Column(Text)
    ordem = Column(Integer, default=0)

    cotacao = relationship("Cotacao", back_populates="itens")
    produto = relationship("Produto")

    __table_args__ = (Index("idx_cotacao_itens_cotacao", "tenant_id", "cotacao_id"),)

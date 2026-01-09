"""
Model de Estoque

Armazena quantidade atual de estoque por produto.
Consumido pelo Stock Intelligence Engine para análises.
"""

from sqlalchemy import Column, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from basecore.db import Base
from construction_app.models.base import BaseModelMixin


class Estoque(Base, BaseModelMixin):
    __tablename__ = "estoque"

    # FK managed by database, not SQLAlchemy (Tenant is in auth service)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    produto_id = Column(
        UUID(as_uuid=True), ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False
    )
    quantidade_atual = Column(Numeric(10, 3), nullable=False, default=0)

    produto = relationship("Produto", backref="estoque")

    __table_args__ = (
        Index("idx_estoque_tenant_produto", "tenant_id", "produto_id", unique=True),
        Index("idx_estoque_tenant", "tenant_id"),
    )

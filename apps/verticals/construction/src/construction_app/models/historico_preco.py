from sqlalchemy import Column, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from basecore.db import Base
from construction_app.models.base import BaseModelMixin


class HistoricoPreco(Base, BaseModelMixin):
    __tablename__ = "historico_precos"

    # FK managed by database, not SQLAlchemy (Tenant/User are in auth service)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    produto_id = Column(
        UUID(as_uuid=True), ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False
    )
    preco = Column(Numeric(10, 2), nullable=False)
    # User FK managed by database (User is in auth service)
    usuario_id = Column(UUID(as_uuid=True), index=True)

    produto = relationship("Produto", back_populates="historico_precos")

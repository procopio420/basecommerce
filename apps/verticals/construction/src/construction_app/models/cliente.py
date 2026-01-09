from sqlalchemy import Column, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from basecore.db import Base
from construction_app.models.base import BaseModelMixin


class Cliente(Base, BaseModelMixin):
    __tablename__ = "clientes"

    # FK managed by database, not SQLAlchemy (Tenant is in auth service)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tipo = Column(String(2), nullable=False)  # 'PF' ou 'PJ'
    nome = Column(String(255), nullable=False)
    documento = Column(String(20), nullable=False)  # CPF ou CNPJ
    email = Column(String(255))
    telefone = Column(String(20))
    endereco = Column(Text)
    cidade = Column(String(100))
    estado = Column(String(2))
    cep = Column(String(10))
    observacoes = Column(Text)

    obras = relationship("Obra", back_populates="cliente", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_clientes_tenant_documento", "tenant_id", "documento", unique=True),
    )

"""
DTOs (Data Transfer Objects) para Stock Intelligence Engine

Define estruturas de dados genéricas para comunicação com o engine.
Não contém lógica de negócio do vertical.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class RiskLevel(str, Enum):
    """Nível de risco de ruptura"""

    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"


class ProductClass(str, Enum):
    """Classificação ABC do produto"""

    A = "A"
    B = "B"
    C = "C"


@dataclass
class SaleEvent:
    """Evento de venda para alimentar histórico"""

    tenant_id: UUID
    pedido_id: UUID
    data_entrega: datetime
    itens: list["SaleItem"]


@dataclass
class SaleItem:
    """Item de venda"""

    produto_id: UUID
    quantidade: Decimal
    valor_total: Decimal


@dataclass
class StockUpdate:
    """Atualização de estoque"""

    tenant_id: UUID
    produto_id: UUID
    quantidade_atual: Decimal
    data_atualizacao: datetime
    tipo_movimento: str  # "entrada", "saida", "ajuste"


@dataclass
class ReplenishmentParameters:
    """Parâmetros de reposição configurados"""

    tenant_id: UUID
    produto_id: UUID
    lead_time_dias: int
    estoque_seguranca_percentual: Decimal
    estoque_minimo_manual: Decimal | None = None
    estoque_maximo_manual: Decimal | None = None


@dataclass
class StockAlert:
    """Alerta de risco de ruptura ou excesso"""

    produto_id: UUID
    tipo: str  # "ruptura", "excesso"
    nivel_risco: RiskLevel
    estoque_atual: Decimal
    estoque_minimo_calculado: Decimal
    dias_ate_ruptura: int | None = None
    explicacao: str = ""


@dataclass
class ReplenishmentSuggestion:
    """Sugestão de reposição de produto"""

    produto_id: UUID
    quantidade_sugerida: Decimal
    estoque_atual: Decimal
    estoque_minimo_calculado: Decimal
    estoque_maximo_sugerido: Decimal
    prioridade: str  # "alta", "media", "baixa"
    explicacao: str = ""


@dataclass
class ABCAnalysis:
    """Análise ABC do produto"""

    produto_id: UUID
    classe: ProductClass
    percentual_vendas_acumulado: Decimal
    percentual_produtos_acumulado: Decimal
    explicacao: str = ""

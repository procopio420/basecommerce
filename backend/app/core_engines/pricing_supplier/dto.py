"""
DTOs (Data Transfer Objects) para Pricing & Supplier Intelligence Engine

Define estruturas de dados genéricas para comunicação com o engine.
Não contém lógica de negócio do vertical.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class SupplierPrice:
    """Preço de fornecedor para um produto"""

    tenant_id: UUID
    produto_id: UUID
    fornecedor_id: UUID
    preco: Decimal
    unidade: str
    data_preco: datetime
    condicoes: Optional["PriceConditions"] = None


@dataclass
class PriceConditions:
    """Condições do preço (quantidade mínima, prazo, etc.)"""

    quantidade_minima: Decimal | None = None
    prazo_pagamento: int | None = None  # dias
    validade_preco: datetime | None = None


@dataclass
class PriceUpdate:
    """Atualização de preço de fornecedor"""

    tenant_id: UUID
    produto_id: UUID
    fornecedor_id: UUID
    preco_anterior: Decimal
    preco_novo: Decimal
    variacao_percentual: Decimal
    data_atualizacao: datetime
    motivo: str | None = None


@dataclass
class SupplierComparison:
    """Comparação de fornecedores para um produto"""

    produto_id: UUID
    fornecedores: list["SupplierComparisonItem"]


@dataclass
class SupplierComparisonItem:
    """Item de comparação de fornecedor"""

    fornecedor_id: UUID
    preco_atual: Decimal
    variacao_vs_mais_barato: Decimal  # percentual
    preco_medio_historico: Decimal | None = None
    estabilidade_preco: str = "estavel"  # "estavel", "instavel"


@dataclass
class SupplierSuggestion:
    """Sugestão de fornecedor mais vantajoso"""

    produto_id: UUID
    fornecedor_recomendado_id: UUID
    preco_recomendado: Decimal
    custo_base: Decimal
    explicacao: str = ""
    alternativas: list["SupplierComparisonItem"] = None


@dataclass
class BaseCost:
    """Custo base de um produto (preço médio ou preço recomendado)"""

    produto_id: UUID
    custo_base: Decimal
    fornecedor_usado_id: UUID | None = None
    data_ultima_atualizacao: datetime = None


@dataclass
class PriceVariationAlert:
    """Alerta de variação de preço"""

    produto_id: UUID
    fornecedor_id: UUID
    preco_anterior: Decimal
    preco_atual: Decimal
    variacao_percentual: Decimal
    tipo_alerta: str  # "aumento", "diminuicao"
    explicacao: str = ""


@dataclass
class PriceTrend:
    """Tendência de preço ao longo do tempo"""

    produto_id: UUID
    fornecedor_id: UUID
    tendencia: str  # "aumento", "diminuicao", "estavel"
    variacao_percentual_periodo: Decimal
    previsao_simples: str | None = None  # ex: "Tendência de aumento: +2% ao mês"

"""
DTOs (Data Transfer Objects) para Sales Intelligence Engine

Define estruturas de dados genéricas para comunicação com o engine.
Não contém lógica de negócio do vertical.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class SuggestionType(str, Enum):
    """Tipo de sugestão"""

    COMPLEMENTAR = "complementar"
    SUBSTITUTO = "substituto"
    BUNDLE = "bundle"


class Priority(str, Enum):
    """Prioridade da sugestão"""

    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


@dataclass
class SaleEvent:
    """Evento de venda concluída para alimentar histórico"""

    tenant_id: UUID
    pedido_id: UUID
    produtos_vendidos: list["SoldProduct"]
    valor_total_pedido: Decimal
    cotacao_id: UUID | None = None
    cliente_id: UUID | None = None
    data_venda: datetime | None = None


@dataclass
class SoldProduct:
    """Produto vendido"""

    produto_id: UUID
    quantidade: Decimal
    preco_unitario: Decimal
    valor_total: Decimal
    foi_sugerido: bool = False
    sugestao_id: UUID | None = None


@dataclass
class SuggestionContext:
    """Contexto para solicitar sugestões"""

    tenant_id: UUID
    contexto: str  # "criando_cotacao", "finalizando_pedido"
    cliente_id: UUID | None = None
    produtos_carrinho: list["CartProduct"] = None
    categoria_contexto: str | None = None  # "obra", "cliente_recorrente", "nova_obra"


@dataclass
class CartProduct:
    """Produto no carrinho/cotação"""

    produto_id: UUID
    quantidade: Decimal


@dataclass
class ProductSuggestion:
    """Sugestão de produto"""

    produto_sugerido_id: UUID
    tipo: SuggestionType
    frequencia: Decimal  # percentual de vezes que é comprado junto
    explicacao: str
    prioridade: Priority
    produto_original_id: UUID | None = None  # para substitutos
    motivo: str | None = None  # para substitutos


@dataclass
class BundleSuggestion:
    """Sugestão de bundle (pacote de produtos)"""

    bundle_id: UUID
    produtos: list[UUID]
    frequencia: Decimal  # percentual de vezes que são vendidos juntos
    explicacao: str
    nome_bundle: str | None = None
    desconto_sugerido: Decimal | None = None  # futuro


@dataclass
class PurchasePattern:
    """Padrão de compra identificado"""

    padrao_id: UUID
    produtos: list[UUID]
    frequencia: Decimal  # percentual de vezes que padrão ocorre
    explicacao: str
    contexto: str | None = None  # por cliente, por período, etc.


@dataclass
class SuggestionFollowed:
    """Feedback: Sugestão seguida pelo usuário"""

    tenant_id: UUID
    sugestao_id: UUID
    tipo_sugestao: SuggestionType
    produto_sugerido_id: UUID
    produto_original_id: UUID | None = None
    contexto_carrinho: list[CartProduct] | None = None
    timestamp: datetime | None = None


@dataclass
class SuggestionIgnored:
    """Feedback: Sugestão ignorada pelo usuário"""

    tenant_id: UUID
    sugestao_id: UUID
    tipo_sugestao: SuggestionType
    produto_sugerido_id: UUID
    contexto_carrinho: list[CartProduct] | None = None
    timestamp: datetime | None = None


@dataclass
class UnavailableProduct:
    """Produto indisponível (solicitação de substituto)"""

    tenant_id: UUID
    produto_id: UUID
    quantidade_desejada: Decimal
    motivo: str  # "sem_estoque", "produto_inativo"
    contexto_carrinho: list[CartProduct] | None = None

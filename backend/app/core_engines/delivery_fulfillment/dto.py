"""
DTOs (Data Transfer Objects) para Delivery & Fulfillment Engine

Define estruturas de dados genéricas para comunicação com o engine.
Não contém lógica de negócio do vertical.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID


class DeliveryStatus(str, Enum):
    """Status da entrega"""

    PENDENTE = "pendente"
    EM_PREPARACAO = "em_preparacao"
    SAIU_ENTREGA = "saiu_entrega"
    CHEGOU = "chegou"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class OccurrenceType(str, Enum):
    """Tipo de ocorrência durante entrega"""

    FALTOU_ITEM = "faltou_item"
    ITEM_ERRADO = "item_errado"
    CLIENTE_NAO_ENCONTRADO = "cliente_nao_encontrado"
    RECUSA = "recusa"
    OUTRO = "outro"


@dataclass
class DeliveryAddress:
    """Endereço de entrega"""

    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str
    coordenadas_gps: Optional["GPSLocation"] = None
    instrucoes_acesso: str | None = None
    horario_preferencial: str | None = None


@dataclass
class GPSLocation:
    """Localização GPS"""

    latitude: Decimal
    longitude: Decimal


@dataclass
class DeliveryProduct:
    """Produto a ser entregue"""

    produto_id: UUID
    quantidade: Decimal
    peso: Decimal | None = None
    volume: Decimal | None = None


@dataclass
class ReadyForDeliveryOrder:
    """Pedido pronto para entrega"""

    tenant_id: UUID
    pedido_id: UUID
    cliente_id: UUID
    endereco_entrega: DeliveryAddress
    produtos: list[DeliveryProduct]
    obra_id: UUID | None = None
    prioridade: str = "normal"  # "alta", "normal", "baixa"
    observacoes: str | None = None


@dataclass
class DeliveryRoute:
    """Rota de entrega sugerida"""

    rota_id: UUID
    pedidos: list["RouteItem"]
    motorista_sugerido_id: UUID | None = None
    veiculo_sugerido_id: UUID | None = None
    distancia_total_estimada: Decimal | None = None  # km
    tempo_total_estimado: int | None = None  # minutos


@dataclass
class RouteItem:
    """Item da rota (pedido com ordem de entrega)"""

    pedido_id: UUID
    ordem: int
    endereco: DeliveryAddress
    distancia_estimada: Decimal | None = None  # km


@dataclass
class DeliveryStatusUpdate:
    """Atualização de status da entrega"""

    tenant_id: UUID
    delivery_id: UUID
    pedido_id: UUID
    status_anterior: DeliveryStatus
    status_novo: DeliveryStatus
    motorista_id: UUID | None = None
    timestamp: datetime | None = None
    observacoes: str | None = None


@dataclass
class DeliveryProof:
    """Prova de entrega (foto, assinatura)"""

    tenant_id: UUID
    delivery_id: UUID
    pedido_id: UUID
    foto_produtos: str | None = None  # base64 encoded
    assinatura_recebedor: str | None = None  # base64 encoded
    nome_recebedor: str | None = None
    documento_recebedor: str | None = None
    data_hora_entrega: datetime | None = None
    coordenadas_gps: GPSLocation | None = None


@dataclass
class DeliveryOccurrence:
    """Ocorrência durante entrega"""

    tenant_id: UUID
    delivery_id: UUID
    pedido_id: UUID
    tipo_ocorrencia: OccurrenceType
    descricao: str
    motorista_id: UUID | None = None
    timestamp: datetime | None = None
    status_resultante: str = ""  # "entregue_com_divergencia", "nao_entregue"
    produtos_afetados: list["OccurrenceProduct"] | None = None


@dataclass
class OccurrenceProduct:
    """Produto afetado por ocorrência"""

    produto_id: UUID
    quantidade_esperada: Decimal
    quantidade_entregue: Decimal
    diferenca: Decimal


@dataclass
class DeliveryCost:
    """Custo operacional da entrega"""

    tenant_id: UUID
    delivery_id: UUID
    pedido_id: UUID
    custo_operacional: Decimal
    distancia_percorrida: Decimal | None = None  # km (futuro)
    tempo_gasto: int | None = None  # minutos (futuro)
    combustivel: Decimal | None = None  # litros (futuro)
    custo_por_km: Decimal | None = None  # (futuro)


@dataclass
class CompletedDelivery:
    """Entrega finalizada (feed para Stock Intelligence)"""

    tenant_id: UUID
    pedido_id: UUID
    itens_entregues: list["DeliveredItem"]
    data_entrega: datetime | None = None


@dataclass
class DeliveredItem:
    """Item entregue"""

    produto_id: UUID
    quantidade: Decimal
    valor_total: Decimal

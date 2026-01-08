"""
Port (Interface) para Delivery & Fulfillment Engine

Define o contrato que o engine deve implementar.
Usa Ports & Adapters pattern para desacoplar vertical de implementação.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.core_engines.delivery_fulfillment.dto import (
    DeliveryCost,
    DeliveryOccurrence,
    DeliveryProof,
    DeliveryRoute,
    DeliveryStatus,
    DeliveryStatusUpdate,
    ReadyForDeliveryOrder,
)


class DeliveryFulfillmentPort(ABC):
    """
    Interface para Delivery & Fulfillment Engine

    Engine horizontal que gerencia ciclo de entrega.
    Não conhece regras específicas do vertical (Materiais de Construção).
    """

    @abstractmethod
    def plan_routes(
        self,
        orders: list[ReadyForDeliveryOrder],
    ) -> list[DeliveryRoute]:
        """
        Planeja rotas agrupando pedidos por região.

        Chamado quando pedidos estão prontos para entrega.

        Args:
            orders: Lista de pedidos prontos para entrega

        Returns:
            Lista de rotas sugeridas agrupadas por região
        """
        raise NotImplementedError

    @abstractmethod
    def update_delivery_status(
        self,
        status_update: DeliveryStatusUpdate,
    ) -> None:
        """
        Atualiza status da entrega.

        Chamado quando motorista atualiza status (em trânsito, chegou, entregue).

        Args:
            status_update: Dados da atualização de status
        """
        raise NotImplementedError

    @abstractmethod
    def register_delivery_proof(
        self,
        proof: DeliveryProof,
    ) -> None:
        """
        Registra prova de entrega (foto, assinatura).

        Chamado quando motorista finaliza entrega e registra prova.

        Args:
            proof: Dados da prova de entrega
        """
        raise NotImplementedError

    @abstractmethod
    def register_occurrence(
        self,
        occurrence: DeliveryOccurrence,
    ) -> None:
        """
        Registra ocorrência durante entrega.

        Chamado quando ocorre problema durante entrega (divergência, problema de acesso, etc.).

        Args:
            occurrence: Dados da ocorrência
        """
        raise NotImplementedError

    @abstractmethod
    def calculate_delivery_cost(
        self,
        tenant_id: UUID,
        delivery_id: UUID,
    ) -> DeliveryCost:
        """
        Calcula custo operacional da entrega.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            delivery_id: ID da entrega

        Returns:
            Custo operacional da entrega
        """
        raise NotImplementedError

    @abstractmethod
    def get_delivery_status(
        self,
        tenant_id: UUID,
        pedido_id: UUID,
    ) -> DeliveryStatus:
        """
        Retorna status atual da entrega.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            pedido_id: ID do pedido

        Returns:
            Status atual da entrega
        """
        raise NotImplementedError

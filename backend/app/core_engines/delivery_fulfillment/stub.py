"""
Stub implementation para Delivery & Fulfillment Engine

Implementação stub que retorna valores vazios ou lança NotImplementedError.
Usado durante desenvolvimento para preparar contratos sem alterar comportamento do MVP1.
"""

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
from app.core_engines.delivery_fulfillment.ports import DeliveryFulfillmentPort


class DeliveryFulfillmentStub(DeliveryFulfillmentPort):
    """
    Implementação stub do Delivery & Fulfillment Engine

    Retorna valores vazios ou defaults para não alterar comportamento do MVP1.
    TODO: Implementar lógica real do engine no MVP2+
    """

    def plan_routes(
        self,
        orders: list[ReadyForDeliveryOrder],
    ) -> list[DeliveryRoute]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar planejamento de rotas baseado em:
        - Agrupamento por região/endereço próximo
        - Ordenação por ordem de entrega
        - Otimização de distância percorrida (futuro: GPS)
        """
        return []

    def update_delivery_status(
        self,
        status_update: DeliveryStatusUpdate,
    ) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar atualização de status para:
        - Atualizar status da entrega
        - Registrar histórico de mudanças
        - Notificar vertical sobre mudanças (futuro: eventos)
        """
        pass

    def register_delivery_proof(
        self,
        proof: DeliveryProof,
    ) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar registro de prova para:
        - Armazenar foto dos produtos entregues
        - Armazenar assinatura do recebedor
        - Registrar localização GPS (futuro)
        - Marcar entrega como finalizada com prova
        """
        pass

    def register_occurrence(
        self,
        occurrence: DeliveryOccurrence,
    ) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar registro de ocorrência para:
        - Registrar tipo e descrição da ocorrência
        - Associar produtos afetados
        - Atualizar status resultante
        - Gerar alertas para resolução (futuro)
        """
        pass

    def calculate_delivery_cost(
        self,
        tenant_id: UUID,
        delivery_id: UUID,
    ) -> DeliveryCost:
        """
        Stub: Retorna custo zero.

        TODO: Implementar cálculo de custo baseado em:
        - Distância percorrida (futuro: GPS)
        - Tempo gasto (futuro)
        - Combustível (futuro: baseado em distância)
        - Custo operacional por entrega
        """
        from decimal import Decimal

        return DeliveryCost(
            tenant_id=tenant_id,
            delivery_id=delivery_id,
            pedido_id=UUID("00000000-0000-0000-0000-000000000000"),
            custo_operacional=Decimal("0"),
        )

    def get_delivery_status(
        self,
        tenant_id: UUID,
        pedido_id: UUID,
    ) -> DeliveryStatus:
        """
        Stub: Retorna status pendente.

        TODO: Implementar consulta de status baseado em:
        - Status atual armazenado no engine
        - Histórico de mudanças de status
        """
        return DeliveryStatus.PENDENTE

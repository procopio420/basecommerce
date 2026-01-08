"""
Implementação real do Delivery & Fulfillment Engine

Implementa lógica básica de planejamento de rotas e controle de status de entrega.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core_engines.delivery_fulfillment.dto import (
    DeliveryCost,
    DeliveryOccurrence,
    DeliveryProof,
    DeliveryRoute,
    DeliveryStatus,
    DeliveryStatusUpdate,
    ReadyForDeliveryOrder,
    RouteItem,
)
from app.core_engines.delivery_fulfillment.ports import DeliveryFulfillmentPort
from app.models.pedido import Pedido


class DeliveryFulfillmentImplementation(DeliveryFulfillmentPort):
    """
    Implementação real do Delivery & Fulfillment Engine

    Gerencia ciclo de entrega usando dados de Pedido e endereços.
    """

    # Armazena rotas criadas (em memória - futuro: banco)
    _routes: dict = {}

    # Armazena status de entregas (em memória - futuro: banco)
    _delivery_status: dict = {}

    # Armazena provas de entrega (em memória - futuro: banco)
    _delivery_proofs: dict = {}

    def __init__(self, db: Session):
        self.db = db

    def plan_routes(
        self,
        orders: list[ReadyForDeliveryOrder],
    ) -> list[DeliveryRoute]:
        """
        Planeja rotas agrupando pedidos por região (cidade/bairro).
        Agrupa pedidos com endereços próximos (mesma cidade).
        """
        if not orders:
            return []

        # Agrupa pedidos por cidade
        grupos_por_cidade = {}

        for order in orders:
            cidade = order.endereco_entrega.cidade
            if cidade not in grupos_por_cidade:
                grupos_por_cidade[cidade] = []
            grupos_por_cidade[cidade].append(order)

        # Cria uma rota por cidade
        rotas = []

        for cidade, pedidos_cidade in grupos_por_cidade.items():
            rota_id = uuid4()

            # Ordena pedidos por endereço (ordem simples - futuro: GPS)
            route_items = []
            for idx, order in enumerate(pedidos_cidade):
                route_items.append(
                    RouteItem(
                        pedido_id=order.pedido_id,
                        ordem=idx + 1,
                        endereco=order.endereco_entrega,
                        distancia_estimada=None,  # Futuro: GPS
                    )
                )

            rota = DeliveryRoute(
                rota_id=rota_id,
                pedidos=route_items,
                motorista_sugerido_id=None,  # Futuro: atribuição automática
                veiculo_sugerido_id=None,  # Futuro: atribuição automática
                distancia_total_estimada=None,  # Futuro: GPS
                tempo_total_estimado=None,  # Futuro: GPS
            )

            # Armazena rota
            self._routes[str(rota_id)] = rota

            rotas.append(rota)

        return rotas

    def update_delivery_status(
        self,
        status_update: DeliveryStatusUpdate,
    ) -> None:
        """
        Atualiza status da entrega.
        Armazena status e histórico de mudanças.
        """
        # Armazena status atual
        key = f"{status_update.tenant_id}_{status_update.pedido_id}"

        if key not in self._delivery_status:
            self._delivery_status[key] = []

        self._delivery_status[key].append(
            {
                "status": status_update.status_novo,
                "timestamp": status_update.timestamp or datetime.utcnow(),
                "motorista_id": status_update.motorista_id,
                "observacoes": status_update.observacoes,
            }
        )

    def register_delivery_proof(
        self,
        proof: DeliveryProof,
    ) -> None:
        """
        Registra prova de entrega (foto, assinatura).
        Armazena dados de prova.
        """
        key = f"{proof.tenant_id}_{proof.pedido_id}"

        self._delivery_proofs[key] = {
            "foto_produtos": proof.foto_produtos,
            "assinatura_recebedor": proof.assinatura_recebedor,
            "nome_recebedor": proof.nome_recebedor,
            "documento_recebedor": proof.documento_recebedor,
            "data_hora_entrega": proof.data_hora_entrega or datetime.utcnow(),
            "coordenadas_gps": proof.coordenadas_gps,
        }

        # Atualiza status para entregue
        status_update = DeliveryStatusUpdate(
            tenant_id=proof.tenant_id,
            delivery_id=proof.delivery_id,
            pedido_id=proof.pedido_id,
            status_anterior=DeliveryStatus.CHEGOU,
            status_novo=DeliveryStatus.ENTREGUE,
            timestamp=proof.data_hora_entrega or datetime.utcnow(),
        )

        self.update_delivery_status(status_update)

    def register_occurrence(
        self,
        occurrence: DeliveryOccurrence,
    ) -> None:
        """
        Registra ocorrência durante entrega.
        Armazena tipo e descrição da ocorrência.
        """
        key = f"{occurrence.tenant_id}_{occurrence.pedido_id}"

        if key not in self._delivery_status:
            self._delivery_status[key] = []

        # Adiciona ocorrência ao histórico
        self._delivery_status[key].append(
            {
                "tipo": "ocorrencia",
                "tipo_ocorrencia": occurrence.tipo_ocorrencia.value,
                "descricao": occurrence.descricao,
                "timestamp": occurrence.timestamp or datetime.utcnow(),
                "motorista_id": occurrence.motorista_id,
                "status_resultante": occurrence.status_resultante,
                "produtos_afetados": occurrence.produtos_afetados,
            }
        )

    def calculate_delivery_cost(
        self,
        tenant_id: UUID,
        delivery_id: UUID,
    ) -> DeliveryCost:
        """
        Calcula custo operacional da entrega.
        Por enquanto, retorna custo fixo (futuro: GPS para distância/tempo).
        """
        # Futuro: calcular baseado em distância, tempo, combustível
        # Por enquanto, retorna custo fixo estimado

        return DeliveryCost(
            tenant_id=tenant_id,
            delivery_id=delivery_id,
            pedido_id=UUID("00000000-0000-0000-0000-000000000000"),  # Será obtido do pedido
            custo_operacional=Decimal("50.00"),  # Custo fixo estimado
            distancia_percorrida=None,  # Futuro: GPS
            tempo_gasto=None,  # Futuro: GPS
            combustivel=None,  # Futuro: GPS
            custo_por_km=None,  # Futuro: GPS
        )

    def get_delivery_status(
        self,
        tenant_id: UUID,
        pedido_id: UUID,
    ) -> DeliveryStatus:
        """
        Retorna status atual da entrega.
        """
        key = f"{tenant_id}_{pedido_id}"

        if key not in self._delivery_status or not self._delivery_status[key]:
            # Se não há status, verifica status do pedido
            pedido = (
                self.db.query(Pedido)
                .filter(Pedido.tenant_id == tenant_id, Pedido.id == pedido_id)
                .first()
            )

            if not pedido:
                return DeliveryStatus.PENDENTE

            # Mapeia status do pedido para status de entrega
            status_map = {
                "pendente": DeliveryStatus.PENDENTE,
                "em_preparacao": DeliveryStatus.EM_PREPARACAO,
                "saiu_entrega": DeliveryStatus.SAIU_ENTREGA,
                "entregue": DeliveryStatus.ENTREGUE,
                "cancelado": DeliveryStatus.CANCELADO,
            }

            return status_map.get(pedido.status, DeliveryStatus.PENDENTE)

        # Retorna último status registrado
        ultimo_status = self._delivery_status[key][-1]
        status_str = ultimo_status.get("status")

        if isinstance(status_str, str):
            try:
                return DeliveryStatus(status_str)
            except ValueError:
                return DeliveryStatus.PENDENTE

        return DeliveryStatus.PENDENTE

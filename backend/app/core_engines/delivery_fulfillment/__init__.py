"""
Delivery & Fulfillment Engine

Engine horizontal que gerencia o ciclo pedido → entrega → confirmação.
Fornece planejamento de rotas, controle de status e registro de prova de entrega.
"""

from app.core_engines.delivery_fulfillment.implementation import DeliveryFulfillmentImplementation
from app.core_engines.delivery_fulfillment.ports import DeliveryFulfillmentPort
from app.core_engines.delivery_fulfillment.stub import DeliveryFulfillmentStub

__all__ = [
    "DeliveryFulfillmentPort",
    "DeliveryFulfillmentStub",
    "DeliveryFulfillmentImplementation",
]

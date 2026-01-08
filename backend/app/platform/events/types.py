"""
Tipos de Eventos

Define todos os tipos de eventos que podem ser publicados pela plataforma.
"""

from enum import Enum


class EventType(str, Enum):
    """
    Tipos de eventos da plataforma.

    Eventos do Vertical "Materiais de Construção":
    """

    # Eventos do Vertical Materiais de Construção
    QUOTE_CREATED = "quote_created"
    QUOTE_CONVERTED = "quote_converted"
    SALE_RECORDED = "sale_recorded"
    ORDER_STATUS_CHANGED = "order_status_changed"

    # Eventos Futuros (não implementados na Fase 2.4)
    PRODUCT_PRICE_UPDATED = "product_price_updated"
    STOCK_UPDATED = "stock_updated"

    def __str__(self) -> str:
        return self.value

"""
Registro de Handlers de Eventos

Registra todos os handlers dos engines para processamento de eventos.
"""

import logging

from app.platform.engines.delivery_fulfillment.handlers import (
    handle_order_status_changed as delivery_handle_order_status_changed,
)

# Handlers do Delivery & Fulfillment Engine
from app.platform.engines.delivery_fulfillment.handlers import (
    handle_quote_converted as delivery_handle_quote_converted,
)

# Handlers do Sales Intelligence Engine
from app.platform.engines.sales_intelligence.handlers import (
    handle_quote_converted as sales_handle_quote_converted,
)
from app.platform.engines.sales_intelligence.handlers import (
    handle_sale_recorded as sales_handle_sale_recorded,
)

# Handlers do Stock Intelligence Engine
from app.platform.engines.stock_intelligence.handlers import (
    handle_sale_recorded as stock_handle_sale_recorded,
)
from app.platform.events.consume_outbox import register_handler
from app.platform.events.types import EventType

logger = logging.getLogger(__name__)


def register_all_handlers():
    """
    Registra todos os handlers de eventos.

    Esta função deve ser chamada quando o consumer é iniciado.
    """
    # Stock Intelligence Engine
    register_handler(EventType.SALE_RECORDED, stock_handle_sale_recorded)

    # Sales Intelligence Engine
    register_handler(EventType.QUOTE_CONVERTED, sales_handle_quote_converted)
    register_handler(EventType.SALE_RECORDED, sales_handle_sale_recorded)

    # Delivery & Fulfillment Engine
    register_handler(EventType.QUOTE_CONVERTED, delivery_handle_quote_converted)
    register_handler(EventType.ORDER_STATUS_CHANGED, delivery_handle_order_status_changed)

    logger.info("Todos os handlers de eventos foram registrados")


# Auto-registra handlers quando módulo é importado
register_all_handlers()

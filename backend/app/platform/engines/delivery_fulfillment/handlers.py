"""
Handlers do Delivery & Fulfillment Engine

Processa eventos e atualiza modelos do Delivery & Fulfillment Engine.
"""

import logging
from uuid import UUID

from app.core.database import get_db
from app.models.pedido import Pedido

logger = logging.getLogger(__name__)


def handle_quote_converted(tenant_id: UUID, payload: dict) -> None:
    """
    Handler para evento quote_converted.

    Prepara dados para planejamento futuro de entrega.
    Não executa planejamento imediato (aguarda status "saiu_entrega").

    Args:
        tenant_id: UUID do tenant
        payload: Payload do evento quote_converted
    """
    db = next(get_db())
    try:
        order_id = payload.get("order_id")
        work_id = payload.get("work_id")

        # Verifica que pedido existe
        pedido = (
            db.query(Pedido)
            .filter(Pedido.id == UUID(order_id), Pedido.tenant_id == tenant_id)
            .first()
        )

        if not pedido:
            logger.warning(
                f"Pedido não encontrado para evento quote_converted: order_id={order_id}",
                extra={"tenant_id": str(tenant_id), "order_id": order_id},
            )
            return

        # Evento processado com sucesso
        # Em versão futura, aqui podemos preparar dados de entrega,
        # agrupar pedidos por região, etc.
        logger.info(
            f"Pedido preparado para planejamento de entrega: order_id={order_id}",
            extra={"tenant_id": str(tenant_id), "order_id": order_id, "work_id": work_id},
        )

        # Commit não necessário - apenas log (em versão futura, atualizar tabelas de planejamento)

    except Exception as e:
        logger.error(
            "Erro ao processar evento quote_converted",
            extra={"tenant_id": str(tenant_id), "payload": payload, "error": str(e)},
            exc_info=True,
        )
        raise  # Re-levanta para que consumer marque como failed
    finally:
        db.close()


def handle_order_status_changed(tenant_id: UUID, payload: dict) -> None:
    """
    Handler para evento order_status_changed.

    Se novo status for "saiu_entrega", planeja rotas de entrega.
    Atualiza status de entrega.

    Args:
        tenant_id: UUID do tenant
        payload: Payload do evento order_status_changed
    """
    db = next(get_db())
    try:
        order_id = payload.get("order_id")
        new_status = payload.get("new_status")

        # Verifica que pedido existe
        pedido = (
            db.query(Pedido)
            .filter(Pedido.id == UUID(order_id), Pedido.tenant_id == tenant_id)
            .first()
        )

        if not pedido:
            logger.warning(
                f"Pedido não encontrado para evento order_status_changed: order_id={order_id}",
                extra={"tenant_id": str(tenant_id), "order_id": order_id},
            )
            return

        # Se status for "saiu_entrega", planeja rotas (em versão futura)
        if new_status == "saiu_entrega":
            logger.info(
                f"Pedido saiu para entrega - planejamento de rotas: order_id={order_id}",
                extra={"tenant_id": str(tenant_id), "order_id": order_id},
            )
            # Em versão futura, aqui podemos chamar engine de planejamento de rotas,
            # agrupar com outros pedidos da mesma região, etc.

        # Commit não necessário - apenas log (em versão futura, atualizar tabelas de rotas)

    except Exception as e:
        logger.error(
            "Erro ao processar evento order_status_changed",
            extra={"tenant_id": str(tenant_id), "payload": payload, "error": str(e)},
            exc_info=True,
        )
        raise  # Re-levanta para que consumer marque como failed
    finally:
        db.close()

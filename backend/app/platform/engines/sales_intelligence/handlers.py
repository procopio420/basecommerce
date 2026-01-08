"""
Handlers do Sales Intelligence Engine

Processa eventos e atualiza modelos do Sales Intelligence Engine.
"""

import logging
from uuid import UUID

from app.core.database import get_db
from app.models.pedido import Pedido

logger = logging.getLogger(__name__)


def handle_quote_converted(tenant_id: UUID, payload: dict) -> None:
    """
    Handler para evento quote_converted.

    Registra venda no histórico para análise de padrões de compra.
    Atualiza dados de produtos vendidos juntos.

    Args:
        tenant_id: UUID do tenant
        payload: Payload do evento quote_converted
    """
    db = next(get_db())
    try:
        quote_id = payload.get("quote_id")
        order_id = payload.get("order_id")
        client_id = payload.get("client_id")
        items = payload.get("items", [])

        if not items:
            logger.warning(f"Evento quote_converted sem itens: order_id={order_id}")
            return

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
        # Em versão futura, aqui podemos atualizar estatísticas de produtos vendidos juntos,
        # padrões de compra por cliente, etc.
        logger.info(
            f"Venda registrada para análise de padrões: order_id={order_id}",
            extra={
                "tenant_id": str(tenant_id),
                "order_id": order_id,
                "quote_id": quote_id,
                "client_id": client_id,
                "items_count": len(items),
            },
        )

        # Commit não necessário - apenas log (em versão futura, atualizar tabelas de estatísticas)

    except Exception as e:
        logger.error(
            "Erro ao processar evento quote_converted",
            extra={"tenant_id": str(tenant_id), "payload": payload, "error": str(e)},
            exc_info=True,
        )
        raise  # Re-levanta para que consumer marque como failed
    finally:
        db.close()


def handle_sale_recorded(tenant_id: UUID, payload: dict) -> None:
    """
    Handler para evento sale_recorded.

    Finaliza registro de venda e atualiza análise de padrões de compra.
    Recalcula produtos complementares baseado em vendas entregues.

    Args:
        tenant_id: UUID do tenant
        payload: Payload do evento sale_recorded
    """
    db = next(get_db())
    try:
        order_id = payload.get("order_id")
        items = payload.get("items", [])

        if not items:
            logger.warning(f"Evento sale_recorded sem itens: order_id={order_id}")
            return

        # Verifica que pedido existe e está entregue
        pedido = (
            db.query(Pedido)
            .filter(
                Pedido.id == UUID(order_id),
                Pedido.tenant_id == tenant_id,
                Pedido.status == "entregue",
            )
            .first()
        )

        if not pedido:
            logger.warning(
                f"Pedido entregue não encontrado para evento sale_recorded: order_id={order_id}",
                extra={"tenant_id": str(tenant_id), "order_id": order_id},
            )
            return

        # Evento processado com sucesso
        # Em versão futura, aqui podemos recalcular produtos complementares,
        # atualizar frequências de produtos vendidos juntos, etc.
        logger.info(
            f"Venda entregue registrada para análise de padrões: order_id={order_id}",
            extra={"tenant_id": str(tenant_id), "order_id": order_id, "items_count": len(items)},
        )

        # Commit não necessário - apenas log (em versão futura, atualizar tabelas de estatísticas)

    except Exception as e:
        logger.error(
            "Erro ao processar evento sale_recorded",
            extra={"tenant_id": str(tenant_id), "payload": payload, "error": str(e)},
            exc_info=True,
        )
        raise  # Re-levanta para que consumer marque como failed
    finally:
        db.close()

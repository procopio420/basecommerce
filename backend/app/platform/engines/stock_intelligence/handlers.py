"""
Handlers do Stock Intelligence Engine

Processa eventos e atualiza modelos do Stock Intelligence Engine.
"""

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.core.database import get_db
from app.models.estoque import Estoque

logger = logging.getLogger(__name__)


def handle_sale_recorded(tenant_id: UUID, payload: dict) -> None:
    """
    Handler para evento sale_recorded.

    Atualiza estoque reduzindo quantidades baseado nos itens vendidos.
    Cria registro de estoque se não existir.

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

        for item in items:
            product_id = UUID(item["product_id"])
            quantity = Decimal(str(item["quantity"]))

            # Busca ou cria registro de estoque
            estoque = (
                db.query(Estoque)
                .filter(Estoque.tenant_id == tenant_id, Estoque.produto_id == product_id)
                .first()
            )

            if estoque:
                # Reduz estoque
                estoque.quantidade_atual = estoque.quantidade_atual - quantity
                if estoque.quantidade_atual < 0:
                    logger.warning(
                        f"Estoque negativo para produto {product_id}: quantidade_atual={estoque.quantidade_atual}",
                        extra={
                            "tenant_id": str(tenant_id),
                            "produto_id": str(product_id),
                            "quantidade": str(quantity),
                            "order_id": order_id,
                        },
                    )
                    estoque.quantidade_atual = Decimal("0")  # Garante não negativo
                estoque.updated_at = datetime.utcnow()
            else:
                # Cria registro de estoque com quantidade zero (produto vendido mas sem estoque registrado)
                estoque = Estoque(
                    tenant_id=tenant_id,
                    produto_id=product_id,
                    quantidade_atual=Decimal("0")
                    - quantity,  # Negativo indica necessidade de reposição
                )
                db.add(estoque)
                logger.info(
                    f"Criado registro de estoque para produto {product_id} (estoque inicial negativo)",
                    extra={
                        "tenant_id": str(tenant_id),
                        "produto_id": str(product_id),
                        "quantidade": str(quantity),
                        "order_id": order_id,
                    },
                )
                if estoque.quantidade_atual < 0:
                    estoque.quantidade_atual = Decimal("0")

        db.commit()
        logger.info(
            f"Estoque atualizado para ordem {order_id}",
            extra={"tenant_id": str(tenant_id), "order_id": order_id, "items_count": len(items)},
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "Erro ao processar evento sale_recorded",
            extra={"tenant_id": str(tenant_id), "payload": payload, "error": str(e)},
            exc_info=True,
        )
        raise  # Re-levanta para que consumer marque como failed
    finally:
        db.close()

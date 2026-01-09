"""
Publisher de Eventos

API simples para publicar eventos pelo vertical.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from construction_app.platform.events.outbox import write_event as _write_event
from construction_app.platform.events.types import EventType


def publish_event(
    db: Session,
    event_type: EventType,
    tenant_id: UUID,
    payload: dict,
    version: str = "1.0",
) -> None:
    """
    Publica evento no outbox.

    Esta função é a API pública para o vertical publicar eventos.
    Internamente, chama write_event que escreve na tabela event_outbox.

    IMPORTANTE: Esta função DEVE ser chamada dentro da mesma transação
    do write principal para garantir atomicidade (outbox pattern).

    Exemplo de uso:

    ```python
    # Na mesma transação do write principal
    with db.begin():
        # Write principal
        pedido = criar_pedido(...)

        # Publica evento na mesma transação
        publish_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant_id,
            payload={
                "quote_id": str(cotacao.id),
                "order_id": str(pedido.id),
                # ... resto do payload
            }
        )

        # COMMIT garante atomicidade de ambos
    ```

    Args:
        db: Sessão do banco de dados (deve estar em uma transação)
        event_type: Tipo do evento (enum EventType)
        tenant_id: UUID do tenant (isolamento multi-tenant)
        payload: Payload do evento (dicionário JSON-serializable)
        version: Versão do contrato do evento (default: "1.0")

    Raises:
        RuntimeError: Se não estiver em uma transação
        ValueError: Se payload não for JSON-serializable
    """
    _write_event(
        db=db,
        event_type=event_type,
        tenant_id=tenant_id,
        payload=payload,
        version=version,
    )

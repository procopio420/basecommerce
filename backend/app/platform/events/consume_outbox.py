"""
Consumer de Eventos do Outbox

Processa eventos pendentes do outbox e chama handlers apropriados.
"""

import logging
from collections.abc import Callable
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.platform.events.outbox import (
    get_pending_events,
    mark_failed,
    mark_processed,
    mark_processing,
)
from app.platform.events.types import EventType

logger = logging.getLogger(__name__)

# Registry de handlers por event_type
_event_handlers: dict[str, list[Callable]] = {}


def register_handler(event_type: EventType, handler: Callable[[UUID, dict], None]):
    """
    Registra handler para um tipo de evento.

    Args:
        event_type: Tipo do evento (enum EventType)
        handler: Função que recebe (tenant_id: UUID, payload: dict) e processa o evento
    """
    event_type_str = str(event_type)
    if event_type_str not in _event_handlers:
        _event_handlers[event_type_str] = []

    _event_handlers[event_type_str].append(handler)
    logger.info(f"Handler registrado para evento: {event_type_str}")


def process_event(event_id: UUID, event_type: str, tenant_id: UUID, payload: dict) -> bool:
    """
    Processa um evento específico chamando todos os handlers registrados.

    IMPORTANTE: Handlers recebem tenant_id e payload, mas NÃO recebem db.
    Handlers devem criar suas próprias sessões de banco de dados.

    Args:
        event_id: UUID do evento
        event_type: Tipo do evento (string)
        tenant_id: UUID do tenant
        payload: Payload do evento

    Returns:
        bool: True se processado com sucesso, False se houve erro
    """
    if event_type not in _event_handlers:
        logger.warning(f"Nenhum handler registrado para evento: {event_type}")
        return True  # Não é erro - apenas não há handlers

    handlers = _event_handlers[event_type]

    if not handlers:
        logger.warning(f"Nenhum handler registrado para evento: {event_type}")
        return True  # Não é erro - apenas não há handlers

    # Chama todos os handlers registrados
    for handler in handlers:
        try:
            handler(tenant_id=tenant_id, payload=payload)
            logger.debug(f"Handler processou evento {event_id} com sucesso")
        except Exception as e:
            logger.error(
                f"Erro ao processar evento {event_id} com handler {handler.__name__}",
                extra={
                    "event_id": str(event_id),
                    "event_type": event_type,
                    "tenant_id": str(tenant_id),
                    "handler": handler.__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            return False  # Falha em qualquer handler = falha geral

    return True  # Todos os handlers executaram com sucesso


def consume_outbox(
    db: Session,
    limit: int = 100,
    tenant_id: UUID | None = None,
    max_retries: int = 3,
) -> int:
    """
    Processa eventos pendentes do outbox.

    Este é o consumer principal que:
    1. Busca eventos pending
    2. Marca como processing (lock)
    3. Processa chamando handlers
    4. Marca como processed ou failed

    Args:
        db: Sessão do banco de dados
        limit: Limite de eventos a processar (default: 100)
        tenant_id: Opcional - processar apenas eventos de um tenant específico
        max_retries: Número máximo de tentativas (default: 3)

    Returns:
        int: Número de eventos processados com sucesso
    """
    # Busca eventos pending
    events = get_pending_events(db=db, limit=limit, tenant_id=tenant_id)

    if not events:
        logger.debug("Nenhum evento pendente encontrado")
        return 0

    logger.info(f"Processando {len(events)} eventos pendentes")

    processed_count = 0

    for event in events:
        try:
            # Marca como processing (com lock pessimista)
            event_processing = mark_processing(db=db, event_id=event.event_id)

            if not event_processing:
                # Evento já foi processado por outro consumer
                logger.debug(f"Evento {event.event_id} já está sendo processado ou não existe")
                continue

            # Processa evento chamando handlers
            success = process_event(
                event_id=event.event_id,
                event_type=event.event_type,
                tenant_id=event.tenant_id,
                payload=event.payload,
            )

            if success:
                # Marca como processed
                mark_processed(db=db, event_id=event.event_id)
                processed_count += 1
                logger.info(f"Evento {event.event_id} processado com sucesso")
            else:
                # Marca como failed (com retry se necessário)
                mark_failed(
                    db=db,
                    event_id=event.event_id,
                    error_message="Erro ao processar evento com handlers",
                    max_retries=max_retries,
                )
                logger.warning(f"Evento {event.event_id} falhou ao processar")

        except Exception as e:
            # Erro crítico - marca como failed
            logger.error(
                f"Erro crítico ao processar evento {event.event_id}",
                extra={
                    "event_id": str(event.event_id),
                    "event_type": event.event_type,
                    "error": str(e),
                },
                exc_info=True,
            )
            try:
                mark_failed(
                    db=db,
                    event_id=event.event_id,
                    error_message=f"Erro crítico: {str(e)}",
                    max_retries=max_retries,
                )
            except Exception as mark_error:
                logger.error(f"Erro ao marcar evento como failed: {mark_error}")

    logger.info(f"Processamento concluído: {processed_count}/{len(events)} eventos processados")

    return processed_count


def run_consumer(limit: int = 100, tenant_id: UUID | None = None):
    """
    Runner principal do consumer.

    Esta função pode ser chamada por:
    - Comando CLI (ex: python -m app.platform.events.consume_outbox)
    - Cron job
    - Background worker (futuro: Celery)

    IMPORTANTE: Handlers devem ser registrados antes de chamar esta função.

    Args:
        limit: Limite de eventos a processar por execução
        tenant_id: Opcional - processar apenas eventos de um tenant específico
    """
    # Garante que handlers estão registrados
    from app.platform.events.register_handlers import register_all_handlers

    register_all_handlers()

    db = next(get_db())
    try:
        count = consume_outbox(db=db, limit=limit, tenant_id=tenant_id)
        logger.info(f"Consumer executado: {count} eventos processados")
        return count
    finally:
        db.close()


if __name__ == "__main__":
    # Permite executar diretamente: python -m app.platform.events.consume_outbox
    import sys

    from app.core.logging import setup_logging

    setup_logging()

    # Registra todos os handlers
    from app.platform.events.register_handlers import register_all_handlers

    register_all_handlers()

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    tenant_id = UUID(sys.argv[2]) if len(sys.argv) > 2 else None

    count = run_consumer(limit=limit, tenant_id=tenant_id)
    sys.exit(0 if count > 0 else 1)

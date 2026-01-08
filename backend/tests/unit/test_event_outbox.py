"""
Testes unitários para Event Outbox

Garante que o Outbox Pattern funciona corretamente.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.platform.events.outbox import (
    OutboxStatus,
    get_pending_events,
    mark_failed,
    mark_processed,
    mark_processing,
    write_event,
)
from app.platform.events.types import EventType


def test_write_event_in_transaction(db, tenant):
    """Testa que evento pode ser escrito em transação"""
    with db.begin():
        event = write_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant.id,
            payload={"quote_id": str(uuid4()), "order_id": str(uuid4()), "items": []},
            version="1.0",
        )

        assert event is not None
        assert event.event_type == "quote_converted"
        assert event.tenant_id == tenant.id
        assert event.status == OutboxStatus.PENDING
        assert event.event_id is not None

    # Após commit, verifica que evento está no banco
    db.refresh(event)
    assert event.status == OutboxStatus.PENDING


def test_write_event_outside_transaction_raises_error(db, tenant):
    """Testa que escrever evento fora de transação levanta erro"""
    with pytest.raises(RuntimeError, match="transação"):
        write_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant.id,
            payload={"test": "data"},
        )


def test_get_pending_events_tenant_isolation(db, tenant):
    """Testa que get_pending_events respeita isolamento de tenant"""
    from app.models.tenant import Tenant

    # Cria segundo tenant
    tenant2 = Tenant(nome="Loja 2", cnpj="98765432000111", email="loja2@teste.com", ativo=True)
    db.add(tenant2)
    db.commit()

    # Escreve eventos para ambos tenants
    with db.begin():
        event1 = write_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant.id,
            payload={"test": "tenant1"},
        )

    with db.begin():
        write_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant2.id,
            payload={"test": "tenant2"},
        )

    # Busca apenas eventos do tenant1
    pending = get_pending_events(db=db, tenant_id=tenant.id)

    assert len(pending) == 1
    assert pending[0].event_id == event1.event_id
    assert pending[0].tenant_id == tenant.id


def test_mark_processing_marks_as_processing(db, tenant):
    """Testa que mark_processing marca evento como processing"""
    with db.begin():
        event = write_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant.id,
            payload={"test": "data"},
        )
        event_id = event.event_id

    # Marca como processing
    processing_event = mark_processing(db=db, event_id=event_id)

    assert processing_event is not None
    assert processing_event.status == OutboxStatus.PROCESSING


def test_mark_processed_marks_as_processed(db, tenant):
    """Testa que mark_processed marca evento como processed"""
    with db.begin():
        event = write_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant.id,
            payload={"test": "data"},
        )
        event_id = event.event_id

    # Marca como processing primeiro
    mark_processing(db=db, event_id=event_id)

    # Marca como processed
    processed_event = mark_processed(db=db, event_id=event_id)

    assert processed_event is not None
    assert processed_event.status == OutboxStatus.PROCESSED
    assert processed_event.processed_at is not None


def test_mark_failed_retries_on_retry_count_less_than_max(db, tenant):
    """Testa que mark_failed retry se retry_count < max_retries"""
    with db.begin():
        event = write_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant.id,
            payload={"test": "data"},
        )
        event_id = event.event_id

    # Marca como processing primeiro
    mark_processing(db=db, event_id=event_id)

    # Marca como failed (retry_count = 1 < max_retries = 3)
    failed_event = mark_failed(db=db, event_id=event_id, error_message="Test error", max_retries=3)

    assert failed_event is not None
    assert failed_event.status == OutboxStatus.PENDING  # Retry
    assert failed_event.retry_count == 1
    assert failed_event.error_message is not None


def test_mark_failed_marks_as_failed_on_max_retries(db, tenant):
    """Testa que mark_failed marca como failed se retry_count >= max_retries"""
    with db.begin():
        event = write_event(
            db=db,
            event_type=EventType.QUOTE_CONVERTED,
            tenant_id=tenant.id,
            payload={"test": "data"},
        )
        event_id = event.event_id

    # Simula 3 tentativas (marca como failed 3 vezes)
    mark_processing(db=db, event_id=event_id)
    mark_failed(db=db, event_id=event_id, error_message="Error 1", max_retries=3)

    mark_processing(db=db, event_id=event_id)
    mark_failed(db=db, event_id=event_id, error_message="Error 2", max_retries=3)

    mark_processing(db=db, event_id=event_id)
    failed_event = mark_failed(db=db, event_id=event_id, error_message="Error 3", max_retries=3)

    assert failed_event is not None
    assert failed_event.status == OutboxStatus.FAILED
    assert failed_event.retry_count == 3
    assert failed_event.failed_at is not None

"""
Testes de integração para Event Handlers

Garante que handlers processam eventos corretamente.
"""

from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.models.estoque import Estoque
from app.models.pedido import Pedido, PedidoItem
from app.models.produto import Produto
from app.platform.engines.stock_intelligence.handlers import (
    handle_sale_recorded as stock_handle_sale_recorded,
)
from app.platform.events.consume_outbox import (
    consume_outbox,
    register_handler,
)
from app.platform.events.publisher import publish_event
from app.platform.events.types import EventType


@pytest.fixture(scope="function")
def register_stock_handler():
    """Registra handler do Stock Intelligence para testes"""
    register_handler(EventType.SALE_RECORDED, stock_handle_sale_recorded)
    yield
    # Limpa handlers após teste (em produção, handlers são registrados uma vez)


def test_sale_recorded_event_processed_by_stock_handler(
    db, tenant, produto, cliente, register_stock_handler
):
    """Testa que evento sale_recorded é processado pelo handler do Stock Intelligence"""
    # Cria pedido entregue com itens
    pedido = Pedido(
        tenant_id=tenant.id,
        cliente_id=cliente.id,
        numero="PED-001",
        status="entregue",
    )
    db.add(pedido)
    db.flush()

    pedido_item = PedidoItem(
        tenant_id=tenant.id,
        pedido_id=pedido.id,
        produto_id=produto.id,
        quantidade=Decimal("10"),
        preco_unitario=Decimal("32.00"),
        valor_total=Decimal("320.00"),
    )
    db.add(pedido_item)
    db.commit()

    # Cria estoque inicial
    estoque = Estoque(
        tenant_id=tenant.id,
        produto_id=produto.id,
        quantidade_atual=Decimal("100"),
    )
    db.add(estoque)
    db.commit()

    # Publica evento sale_recorded (na mesma transação)
    with db.begin():
        publish_event(
            db=db,
            event_type=EventType.SALE_RECORDED,
            tenant_id=tenant.id,
            payload={
                "order_id": str(pedido.id),
                "items": [
                    {
                        "product_id": str(produto.id),
                        "quantity": "10.000",
                        "unit_price": "32.00",
                        "total_value": "320.00",
                    }
                ],
            },
        )

    # Processa eventos
    processed_count = consume_outbox(db=db, limit=10, tenant_id=tenant.id)

    assert processed_count == 1

    # Verifica que estoque foi atualizado
    estoque_atualizado = (
        db.query(Estoque)
        .filter(Estoque.tenant_id == tenant.id, Estoque.produto_id == produto.id)
        .first()
    )

    assert estoque_atualizado is not None
    assert estoque_atualizado.quantidade_atual == Decimal("90")  # 100 - 10


def test_event_tenant_isolation_in_handlers(
    db, tenant, tenant2, produto, produto2, cliente, register_stock_handler
):
    """Testa que handlers respeitam isolamento multi-tenant"""
    from app.models.tenant import Tenant

    # Cria pedidos para ambos tenants
    pedido1 = Pedido(
        tenant_id=tenant.id,
        cliente_id=cliente.id,
        numero="PED-001",
        status="entregue",
    )
    db.add(pedido1)
    db.flush()

    pedido_item1 = PedidoItem(
        tenant_id=tenant.id,
        pedido_id=pedido1.id,
        produto_id=produto.id,
        quantidade=Decimal("10"),
        preco_unitario=Decimal("32.00"),
        valor_total=Decimal("320.00"),
    )
    db.add(pedido_item1)

    pedido2 = Pedido(
        tenant_id=tenant2.id,
        cliente_id=cliente.id,  # Mesmo cliente, mas tenant diferente
        numero="PED-002",
        status="entregue",
    )
    db.add(pedido2)
    db.flush()

    pedido_item2 = PedidoItem(
        tenant_id=tenant2.id,
        pedido_id=pedido2.id,
        produto_id=produto2.id,
        quantidade=Decimal("5"),
        preco_unitario=Decimal("20.00"),
        valor_total=Decimal("100.00"),
    )
    db.add(pedido_item2)
    db.commit()

    # Cria estoques para ambos tenants
    estoque1 = Estoque(
        tenant_id=tenant.id,
        produto_id=produto.id,
        quantidade_atual=Decimal("100"),
    )
    db.add(estoque1)

    estoque2 = Estoque(
        tenant_id=tenant2.id,
        produto_id=produto2.id,
        quantidade_atual=Decimal("50"),
    )
    db.add(estoque2)
    db.commit()

    # Publica eventos para ambos tenants
    with db.begin():
        publish_event(
            db=db,
            event_type=EventType.SALE_RECORDED,
            tenant_id=tenant.id,
            payload={
                "order_id": str(pedido1.id),
                "items": [
                    {
                        "product_id": str(produto.id),
                        "quantity": "10.000",
                        "unit_price": "32.00",
                        "total_value": "320.00",
                    }
                ],
            },
        )

    with db.begin():
        publish_event(
            db=db,
            event_type=EventType.SALE_RECORDED,
            tenant_id=tenant2.id,
            payload={
                "order_id": str(pedido2.id),
                "items": [
                    {
                        "product_id": str(produto2.id),
                        "quantity": "5.000",
                        "unit_price": "20.00",
                        "total_value": "100.00",
                    }
                ],
            },
        )

    # Processa apenas eventos do tenant1
    processed_count = consume_outbox(db=db, limit=10, tenant_id=tenant.id)

    assert processed_count == 1

    # Verifica que apenas estoque do tenant1 foi atualizado
    estoque1_atualizado = (
        db.query(Estoque)
        .filter(Estoque.tenant_id == tenant.id, Estoque.produto_id == produto.id)
        .first()
    )

    assert estoque1_atualizado.quantidade_atual == Decimal("90")  # 100 - 10

    estoque2_atualizado = (
        db.query(Estoque)
        .filter(Estoque.tenant_id == tenant2.id, Estoque.produto_id == produto2.id)
        .first()
    )

    assert estoque2_atualizado.quantidade_atual == Decimal("50")  # Não alterado

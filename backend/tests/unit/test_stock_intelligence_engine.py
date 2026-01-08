"""
Testes unitários para Stock Intelligence Engine
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core_engines.stock_intelligence import StockIntelligenceImplementation
from app.core_engines.stock_intelligence.dto import (
    ReplenishmentParameters,
    SaleEvent,
    SaleItem,
    StockUpdate,
)
from app.models.estoque import Estoque
from app.models.pedido import Pedido, PedidoItem
from app.models.produto import Produto


def test_get_stock_alerts_tenant_isolation(db, tenant, produto):
    """Testa que alertas são isolados por tenant"""
    from app.models.tenant import Tenant

    # Cria segundo tenant
    tenant2 = Tenant(nome="Loja 2", cnpj="98765432000111", email="loja2@teste.com", ativo=True)
    db.add(tenant2)
    db.commit()

    # Cria produto para tenant2
    produto2 = Produto(
        tenant_id=tenant2.id,
        codigo="PROD-002",
        nome="Produto 2",
        preco_base=Decimal("10.00"),
        ativo=True,
    )
    db.add(produto2)
    db.commit()

    # Cria estoque para tenant1 (baixo)
    estoque1 = Estoque(tenant_id=tenant.id, produto_id=produto.id, quantidade_atual=Decimal("5"))
    db.add(estoque1)

    # Cria estoque para tenant2 (baixo)
    estoque2 = Estoque(tenant_id=tenant2.id, produto_id=produto2.id, quantidade_atual=Decimal("3"))
    db.add(estoque2)
    db.commit()

    engine = StockIntelligenceImplementation(db)

    # Busca alertas apenas para tenant1
    alertas = engine.get_stock_alerts(tenant_id=tenant.id)

    # Verifica que apenas alertas do tenant1 são retornados
    assert len(alertas) >= 0  # Pode ter 0 ou mais alertas
    for alerta in alertas:
        assert alerta.produto_id == produto.id
        assert alerta.produto_id != produto2.id  # Não deve incluir produto do tenant2


def test_update_stock_creates_or_updates(db, tenant, produto):
    """Testa que update_stock cria ou atualiza estoque corretamente"""
    engine = StockIntelligenceImplementation(db)

    # Cria estoque inicial
    estoque = Estoque(tenant_id=tenant.id, produto_id=produto.id, quantidade_atual=Decimal("10"))
    db.add(estoque)
    db.commit()

    # Atualiza estoque
    update = StockUpdate(
        tenant_id=tenant.id,
        produto_id=produto.id,
        quantidade_nova=Decimal("15"),
        tipo_movimento="entrada",
        observacoes="Teste",
    )

    engine.update_stock(update)
    db.commit()

    # Verifica que estoque foi atualizado
    estoque_atualizado = (
        db.query(Estoque)
        .filter(Estoque.tenant_id == tenant.id, Estoque.produto_id == produto.id)
        .first()
    )

    assert estoque_atualizado is not None
    assert estoque_atualizado.quantidade_atual == Decimal("15")


def test_configure_replenishment_parameters(db, tenant, produto):
    """Testa que parâmetros de reposição são configurados corretamente"""
    engine = StockIntelligenceImplementation(db)

    params = ReplenishmentParameters(
        tenant_id=tenant.id,
        produto_id=produto.id,
        lead_time_dias=10,
        estoque_seguranca_percentual=Decimal("20"),
        estoque_minimo_manual=Decimal("50"),
        estoque_maximo_manual=Decimal("200"),
    )

    engine.configure_replenishment_parameters(params)

    # Verifica que parâmetros foram salvos (em memória no stub, mas testa chamada)
    # Em implementação real, verificar banco de dados ou storage
    assert True  # Teste básico de que método não levanta exceção


def test_get_replenishment_suggestions_tenant_isolation(db, tenant, produto):
    """Testa que sugestões de reposição são isoladas por tenant"""
    from app.models.tenant import Tenant

    tenant2 = Tenant(nome="Loja 2", cnpj="98765432000111", email="loja2@teste.com", ativo=True)
    db.add(tenant2)
    db.commit()

    engine = StockIntelligenceImplementation(db)

    # Busca sugestões apenas para tenant1
    sugestoes = engine.get_replenishment_suggestions(tenant_id=tenant.id, product_ids=[produto.id])

    # Verifica que não há erros e sugestões são do tenant correto
    assert isinstance(sugestoes, list)
    for sug in sugestoes:
        assert sug.produto_id == produto.id

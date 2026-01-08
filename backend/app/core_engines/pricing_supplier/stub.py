"""
Stub implementation para Pricing & Supplier Intelligence Engine

Implementação stub que retorna valores vazios ou lança NotImplementedError.
Usado durante desenvolvimento para preparar contratos sem alterar comportamento do MVP1.
"""

from decimal import Decimal
from uuid import UUID

from app.core_engines.pricing_supplier.dto import (
    BaseCost,
    PriceTrend,
    PriceUpdate,
    PriceVariationAlert,
    SupplierComparison,
    SupplierPrice,
    SupplierSuggestion,
)
from app.core_engines.pricing_supplier.ports import PricingSupplierIntelligencePort


class PricingSupplierIntelligenceStub(PricingSupplierIntelligencePort):
    """
    Implementação stub do Pricing & Supplier Intelligence Engine

    Retorna valores vazios ou defaults para não alterar comportamento do MVP1.
    TODO: Implementar lógica real do engine no MVP2+
    """

    def register_price(self, price: SupplierPrice) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar registro de preço para:
        - Armazenar preço atual de fornecedor
        - Atualizar histórico de preços
        - Calcular comparações e tendências
        """
        pass

    def update_price(self, price_update: PriceUpdate) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar atualização de preço para:
        - Atualizar preço no histórico
        - Detectar variações relevantes
        - Gerar alertas de variação
        """
        pass

    def compare_suppliers(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> SupplierComparison:
        """
        Stub: Retorna comparação vazia.

        TODO: Implementar comparação baseado em:
        - Preços atuais de todos os fornecedores do produto
        - Ordenação por preço (menor para maior)
        - Cálculo de variação percentual vs mais barato
        """
        return SupplierComparison(
            produto_id=produto_id,
            fornecedores=[],
        )

    def suggest_supplier(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> SupplierSuggestion:
        """
        Stub: Retorna sugestão vazia.

        TODO: Implementar sugestão baseado em:
        - Preço atual (fornecedor mais barato)
        - Histórico de preços (estabilidade)
        - Consideração de outros fatores (futuro: qualidade, prazo)
        """
        raise NotImplementedError("Sugestão de fornecedor não implementada ainda")

    def get_base_cost(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> BaseCost:
        """
        Stub: Retorna custo base default.

        TODO: Implementar cálculo de custo base baseado em:
        - Preço médio de todos os fornecedores, ou
        - Preço do fornecedor recomendado
        """
        raise NotImplementedError("Custo base não implementado ainda")

    def get_price_alerts(
        self,
        tenant_id: UUID,
        produto_id: UUID | None = None,
    ) -> list[PriceVariationAlert]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar detecção de alertas baseado em:
        - Variações significativas de preço (ex: >10%)
        - Comparação com preço anterior
        - Threshold configurável
        """
        return []

    def get_price_trend(
        self,
        tenant_id: UUID,
        produto_id: UUID,
        fornecedor_id: UUID,
    ) -> PriceTrend:
        """
        Stub: Retorna tendência estável.

        TODO: Implementar análise de tendência baseado em:
        - Histórico de preços ao longo do tempo
        - Detecção de padrões (aumento, diminuição, estável)
        - Previsão simples (futuro)
        """
        return PriceTrend(
            produto_id=produto_id,
            fornecedor_id=fornecedor_id,
            tendencia="estavel",
            variacao_percentual_periodo=Decimal("0"),
        )

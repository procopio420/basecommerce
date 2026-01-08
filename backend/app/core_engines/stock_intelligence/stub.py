"""
Stub implementation para Stock Intelligence Engine

Implementação stub que retorna valores vazios ou lança NotImplementedError.
Usado durante desenvolvimento para preparar contratos sem alterar comportamento do MVP1.
"""

from uuid import UUID

from app.core_engines.stock_intelligence.dto import (
    ABCAnalysis,
    ReplenishmentParameters,
    ReplenishmentSuggestion,
    SaleEvent,
    StockAlert,
    StockUpdate,
)
from app.core_engines.stock_intelligence.ports import StockIntelligencePort


class StockIntelligenceStub(StockIntelligencePort):
    """
    Implementação stub do Stock Intelligence Engine

    Retorna valores vazios para não alterar comportamento do MVP1.
    TODO: Implementar lógica real do engine no MVP2+
    """

    def get_stock_alerts(
        self,
        tenant_id: UUID,
        risk_level: str | None = None,
        product_ids: list[UUID] | None = None,
    ) -> list[StockAlert]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar análise de risco de ruptura baseado em:
        - Histórico de vendas
        - Estoque atual
        - Lead time configurado
        """
        return []

    def get_replenishment_suggestions(
        self,
        tenant_id: UUID,
        product_ids: list[UUID] | None = None,
    ) -> list[ReplenishmentSuggestion]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar cálculo de sugestões baseado em:
        - Vendas históricas (média diária/semanal)
        - Estoque atual
        - Lead time
        - Estoque mínimo/máximo calculado
        """
        return []

    def get_abc_analysis(
        self,
        tenant_id: UUID,
        product_ids: list[UUID] | None = None,
    ) -> list[ABCAnalysis]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar análise ABC baseado em:
        - Histórico de vendas (análise de Pareto)
        - Classificação em classes A, B, C
        """
        return []

    def register_sale(self, sale_event: SaleEvent) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar registro de venda para:
        - Atualizar histórico de vendas
        - Recalcular sugestões de reposição
        - Atualizar análise ABC
        """
        pass

    def update_stock(self, stock_update: StockUpdate) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar atualização de estoque para:
        - Atualizar estoque atual
        - Recalcular alertas de risco
        - Recalcular sugestões de reposição
        """
        pass

    def configure_replenishment_parameters(
        self,
        parameters: ReplenishmentParameters,
    ) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar configuração de parâmetros para:
        - Armazenar lead time por produto
        - Armazenar estoque de segurança
        - Usar parâmetros no cálculo de sugestões
        """
        pass

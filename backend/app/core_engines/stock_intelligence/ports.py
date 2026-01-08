"""
Port (Interface) para Stock Intelligence Engine

Define o contrato que o engine deve implementar.
Usa Ports & Adapters pattern para desacoplar vertical de implementação.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.core_engines.stock_intelligence.dto import (
    ABCAnalysis,
    ReplenishmentParameters,
    ReplenishmentSuggestion,
    SaleEvent,
    StockAlert,
    StockUpdate,
)


class StockIntelligencePort(ABC):
    """
    Interface para Stock Intelligence Engine

    Engine horizontal que fornece inteligência sobre reposição de estoque.
    Não conhece regras específicas do vertical (Materiais de Construção).
    """

    @abstractmethod
    def get_stock_alerts(
        self,
        tenant_id: UUID,
        risk_level: str | None = None,
        product_ids: list[UUID] | None = None,
    ) -> list[StockAlert]:
        """
        Retorna alertas de risco de ruptura ou excesso de estoque.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            risk_level: Filtro opcional por nível de risco ("alto", "medio", "baixo")
            product_ids: Lista opcional de produtos para filtrar

        Returns:
            Lista de alertas de estoque
        """
        raise NotImplementedError

    @abstractmethod
    def get_replenishment_suggestions(
        self,
        tenant_id: UUID,
        product_ids: list[UUID] | None = None,
    ) -> list[ReplenishmentSuggestion]:
        """
        Retorna sugestões de reposição de estoque.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            product_ids: Lista opcional de produtos para filtrar

        Returns:
            Lista de sugestões de reposição
        """
        raise NotImplementedError

    @abstractmethod
    def get_abc_analysis(
        self,
        tenant_id: UUID,
        product_ids: list[UUID] | None = None,
    ) -> list[ABCAnalysis]:
        """
        Retorna análise ABC (classificação de produtos por importância).

        Args:
            tenant_id: ID do tenant (multi-tenant)
            product_ids: Lista opcional de produtos para filtrar

        Returns:
            Lista de análises ABC
        """
        raise NotImplementedError

    @abstractmethod
    def register_sale(self, sale_event: SaleEvent) -> None:
        """
        Registra venda para atualizar histórico de vendas.

        Chamado quando pedido é entregue (pedido entregue = venda concluída).

        Args:
            sale_event: Dados do evento de venda
        """
        raise NotImplementedError

    @abstractmethod
    def update_stock(self, stock_update: StockUpdate) -> None:
        """
        Atualiza estoque atual de um produto.

        Chamado quando estoque é atualizado (entrada, saída, ajuste).

        Args:
            stock_update: Dados da atualização de estoque
        """
        raise NotImplementedError

    @abstractmethod
    def configure_replenishment_parameters(
        self,
        parameters: ReplenishmentParameters,
    ) -> None:
        """
        Configura parâmetros de reposição para um produto.

        Args:
            parameters: Parâmetros de reposição (lead time, estoque de segurança, etc.)
        """
        raise NotImplementedError

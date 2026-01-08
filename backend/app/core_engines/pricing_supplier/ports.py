"""
Port (Interface) para Pricing & Supplier Intelligence Engine

Define o contrato que o engine deve implementar.
Usa Ports & Adapters pattern para desacoplar vertical de implementação.
"""

from abc import ABC, abstractmethod
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


class PricingSupplierIntelligencePort(ABC):
    """
    Interface para Pricing & Supplier Intelligence Engine

    Engine horizontal que fornece inteligência sobre fornecedores e custos.
    Não conhece regras específicas do vertical (Materiais de Construção).
    """

    @abstractmethod
    def register_price(self, price: SupplierPrice) -> None:
        """
        Registra preço de fornecedor para um produto.

        Chamado quando usuário cadastra ou atualiza preço de fornecedor.

        Args:
            price: Dados do preço do fornecedor
        """
        raise NotImplementedError

    @abstractmethod
    def update_price(self, price_update: PriceUpdate) -> None:
        """
        Atualiza preço de fornecedor.

        Chamado quando preço de fornecedor muda.

        Args:
            price_update: Dados da atualização de preço
        """
        raise NotImplementedError

    @abstractmethod
    def compare_suppliers(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> SupplierComparison:
        """
        Compara fornecedores para um produto.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            produto_id: ID do produto

        Returns:
            Comparação de fornecedores ordenada por preço
        """
        raise NotImplementedError

    @abstractmethod
    def suggest_supplier(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> SupplierSuggestion:
        """
        Sugere fornecedor mais vantajoso para um produto.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            produto_id: ID do produto

        Returns:
            Sugestão de fornecedor com custo base
        """
        raise NotImplementedError

    @abstractmethod
    def get_base_cost(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> BaseCost:
        """
        Retorna custo base de um produto (preço médio ou preço recomendado).

        Usado por outros engines (ex: Stock Intelligence) ou pelo vertical.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            produto_id: ID do produto

        Returns:
            Custo base do produto
        """
        raise NotImplementedError

    @abstractmethod
    def get_price_alerts(
        self,
        tenant_id: UUID,
        produto_id: UUID | None = None,
    ) -> list[PriceVariationAlert]:
        """
        Retorna alertas de variação de preço.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            produto_id: ID opcional do produto para filtrar

        Returns:
            Lista de alertas de variação de preço
        """
        raise NotImplementedError

    @abstractmethod
    def get_price_trend(
        self,
        tenant_id: UUID,
        produto_id: UUID,
        fornecedor_id: UUID,
    ) -> PriceTrend:
        """
        Retorna tendência de preço ao longo do tempo.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            produto_id: ID do produto
            fornecedor_id: ID do fornecedor

        Returns:
            Tendência de preço
        """
        raise NotImplementedError

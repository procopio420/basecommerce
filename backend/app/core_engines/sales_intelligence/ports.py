"""
Port (Interface) para Sales Intelligence Engine

Define o contrato que o engine deve implementar.
Usa Ports & Adapters pattern para desacoplar vertical de implementação.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.core_engines.sales_intelligence.dto import (
    BundleSuggestion,
    ProductSuggestion,
    PurchasePattern,
    SaleEvent,
    SuggestionContext,
    SuggestionFollowed,
    SuggestionIgnored,
    UnavailableProduct,
)


class SalesIntelligencePort(ABC):
    """
    Interface para Sales Intelligence Engine

    Engine horizontal que fornece sugestões para aumentar valor de venda.
    Não conhece regras específicas do vertical (Materiais de Construção).
    """

    @abstractmethod
    def get_suggestions(
        self,
        context: SuggestionContext,
    ) -> list[ProductSuggestion]:
        """
        Retorna sugestões de produtos baseadas no contexto atual.

        Chamado durante criação de cotação/pedido quando vendedor adiciona produtos.

        Args:
            context: Contexto atual (produtos no carrinho, cliente, etc.)

        Returns:
            Lista de sugestões de produtos (complementares, substitutos)
        """
        raise NotImplementedError

    @abstractmethod
    def get_complementary_products(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> list[ProductSuggestion]:
        """
        Retorna produtos complementares de um produto.

        Chamado quando vendedor adiciona produto e quer ver o que é comprado junto.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            produto_id: ID do produto

        Returns:
            Lista de produtos complementares
        """
        raise NotImplementedError

    @abstractmethod
    def get_substitute_products(
        self,
        tenant_id: UUID,
        produto_id: UUID,
        unavailable_product: UnavailableProduct,
    ) -> list[ProductSuggestion]:
        """
        Retorna produtos substitutos quando produto está indisponível.

        Chamado quando vendedor tenta adicionar produto que não está disponível.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            produto_id: ID do produto original (indisponível)
            unavailable_product: Dados do produto indisponível

        Returns:
            Lista de produtos substitutos
        """
        raise NotImplementedError

    @abstractmethod
    def get_bundles(
        self,
        tenant_id: UUID,
        context: SuggestionContext | None = None,
    ) -> list[BundleSuggestion]:
        """
        Retorna bundles (pacotes de produtos) sugeridos.

        Chamado quando vertical solicita sugestões de bundles.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            context: Contexto opcional (produtos no carrinho)

        Returns:
            Lista de bundles sugeridos
        """
        raise NotImplementedError

    @abstractmethod
    def get_purchase_patterns(
        self,
        tenant_id: UUID,
        cliente_id: UUID | None = None,
    ) -> list[PurchasePattern]:
        """
        Retorna padrões de compra identificados.

        Chamado quando vertical solicita análise de padrões.

        Args:
            tenant_id: ID do tenant (multi-tenant)
            cliente_id: ID opcional do cliente para filtrar padrões

        Returns:
            Lista de padrões de compra
        """
        raise NotImplementedError

    @abstractmethod
    def register_sale(self, sale_event: SaleEvent) -> None:
        """
        Registra venda concluída para atualizar histórico.

        Chamado quando cotação é convertida em pedido ou pedido é finalizado.

        Args:
            sale_event: Dados do evento de venda
        """
        raise NotImplementedError

    @abstractmethod
    def record_suggestion_followed(self, feedback: SuggestionFollowed) -> None:
        """
        Registra feedback: sugestão foi seguida pelo usuário.

        Chamado quando vendedor adiciona produto sugerido ao carrinho.

        Args:
            feedback: Dados do feedback de sugestão seguida
        """
        raise NotImplementedError

    @abstractmethod
    def record_suggestion_ignored(self, feedback: SuggestionIgnored) -> None:
        """
        Registra feedback: sugestão foi ignorada pelo usuário.

        Chamado quando vendedor descarta sugestão de produto.

        Args:
            feedback: Dados do feedback de sugestão ignorada
        """
        raise NotImplementedError

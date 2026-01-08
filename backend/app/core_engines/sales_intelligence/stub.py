"""
Stub implementation para Sales Intelligence Engine

Implementação stub que retorna valores vazios ou lança NotImplementedError.
Usado durante desenvolvimento para preparar contratos sem alterar comportamento do MVP1.
"""

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
from app.core_engines.sales_intelligence.ports import SalesIntelligencePort


class SalesIntelligenceStub(SalesIntelligencePort):
    """
    Implementação stub do Sales Intelligence Engine

    Retorna valores vazios para não alterar comportamento do MVP1.
    TODO: Implementar lógica real do engine no MVP2+
    """

    def get_suggestions(
        self,
        context: SuggestionContext,
    ) -> list[ProductSuggestion]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar sugestões baseado em:
        - Análise de padrões de compra (produtos frequentemente comprados juntos)
        - Contexto atual (produtos no carrinho)
        - Histórico de vendas
        - Regras simples de associação (não IA pesada inicialmente)
        """
        return []

    def get_complementary_products(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> list[ProductSuggestion]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar produtos complementares baseado em:
        - Frequência de compra junto (ex: 80% compram X e Y juntos)
        - Análise de padrões de associação
        """
        return []

    def get_substitute_products(
        self,
        tenant_id: UUID,
        produto_id: UUID,
        unavailable_product: UnavailableProduct,
    ) -> list[ProductSuggestion]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar produtos substitutos baseado em:
        - Categoria similar
        - Preço similar
        - Uso similar
        """
        return []

    def get_bundles(
        self,
        tenant_id: UUID,
        context: SuggestionContext | None = None,
    ) -> list[BundleSuggestion]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar bundles baseado em:
        - Combinações de produtos frequentemente vendidos juntos
        - Frequência de venda conjunta (ex: 70% vendem A, B e C juntos)
        """
        return []

    def get_purchase_patterns(
        self,
        tenant_id: UUID,
        cliente_id: UUID | None = None,
    ) -> list[PurchasePattern]:
        """
        Stub: Retorna lista vazia.

        TODO: Implementar padrões de compra baseado em:
        - Análise de histórico de vendas
        - Identificação de padrões detectáveis (não ML complexo)
        - Agrupamento por cliente, período, contexto
        """
        return []

    def register_sale(self, sale_event: SaleEvent) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar registro de venda para:
        - Atualizar histórico de vendas
        - Recalcular padrões de compra
        - Atualizar frequências de associação
        - Atualizar sugestões de bundles
        """
        pass

    def record_suggestion_followed(self, feedback: SuggestionFollowed) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar registro de feedback para:
        - Validar se sugestões são úteis (métricas de sucesso)
        - Melhorar algoritmos de sugestão (futuro)
        """
        pass

    def record_suggestion_ignored(self, feedback: SuggestionIgnored) -> None:
        """
        Stub: Não faz nada.

        TODO: Implementar registro de feedback para:
        - Entender por que sugestões não são seguidas
        - Melhorar relevância das sugestões (futuro)
        """
        pass

"""
Implementação real do Sales Intelligence Engine

Implementa lógica básica de sugestões de produtos complementares e bundles.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core_engines.sales_intelligence.dto import (
    BundleSuggestion,
    Priority,
    ProductSuggestion,
    PurchasePattern,
    SaleEvent,
    SuggestionContext,
    SuggestionFollowed,
    SuggestionIgnored,
    SuggestionType,
    UnavailableProduct,
)
from app.core_engines.sales_intelligence.ports import SalesIntelligencePort
from app.models.pedido import Pedido, PedidoItem
from app.models.produto import Produto


class SalesIntelligenceImplementation(SalesIntelligencePort):
    """
    Implementação real do Sales Intelligence Engine

    Usa dados do banco (PedidoItem com status="entregue" para histórico de vendas).
    Analisa padrões simples de associação entre produtos.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_suggestions(
        self,
        context: SuggestionContext,
    ) -> list[ProductSuggestion]:
        """
        Retorna sugestões baseadas nos produtos no carrinho.
        Analisa quais produtos são frequentemente comprados junto com os do carrinho.
        """
        if not context.produtos_carrinho or len(context.produtos_carrinho) == 0:
            return []

        # Coleta IDs dos produtos no carrinho
        produtos_carrinho_ids = [p.produto_id for p in context.produtos_carrinho]

        # Para cada produto no carrinho, busca produtos complementares
        sugestoes_por_produto = {}

        for produto_id in produtos_carrinho_ids:
            complementares = self.get_complementary_products(context.tenant_id, produto_id)
            for sug in complementares:
                # Evita sugerir produtos já no carrinho
                if sug.produto_sugerido_id not in produtos_carrinho_ids:
                    if sug.produto_sugerido_id not in sugestoes_por_produto:
                        sugestoes_por_produto[sug.produto_sugerido_id] = sug
                    else:
                        # Se já existe, mantém a que tem maior frequência
                        if (
                            sug.frequencia
                            > sugestoes_por_produto[sug.produto_sugerido_id].frequencia
                        ):
                            sugestoes_por_produto[sug.produto_sugerido_id] = sug

        # Converte para lista e ordena por prioridade
        sugestoes = list(sugestoes_por_produto.values())
        priority_order = {Priority.ALTA: 0, Priority.MEDIA: 1, Priority.BAIXA: 2}
        sugestoes.sort(key=lambda s: (priority_order.get(s.prioridade, 3), -s.frequencia))

        # Limita a 5 sugestões
        return sugestoes[:5]

    def get_complementary_products(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> list[ProductSuggestion]:
        """
        Retorna produtos frequentemente comprados junto com o produto fornecido.
        Analisa pedidos entregues dos últimos 90 dias.
        """
        data_limite = datetime.utcnow() - timedelta(days=90)

        # Busca todos os pedidos entregues que contêm o produto
        pedidos_com_produto = (
            self.db.query(Pedido.id)
            .join(PedidoItem, PedidoItem.pedido_id == Pedido.id)
            .filter(
                Pedido.tenant_id == tenant_id,
                Pedido.status == "entregue",
                PedidoItem.produto_id == produto_id,
                Pedido.entregue_em >= data_limite,
            )
            .distinct()
            .all()
        )

        pedido_ids = [p[0] for p in pedidos_com_produto]

        if not pedido_ids:
            return []

        # Conta quantas vezes cada outro produto aparece junto
        produtos_junto = defaultdict(int)

        for pedido_id in pedido_ids:
            # Busca todos os produtos deste pedido (exceto o produto original)
            itens = (
                self.db.query(PedidoItem.produto_id)
                .filter(
                    PedidoItem.tenant_id == tenant_id,  # Garantir isolamento multi-tenant
                    PedidoItem.pedido_id == pedido_id,
                    PedidoItem.produto_id != produto_id,
                )
                .distinct()
                .all()
            )

            for item in itens:
                produtos_junto[item[0]] += 1

        # Calcula frequência (percentual)
        total_pedidos = len(pedido_ids)
        if total_pedidos == 0:
            return []

        sugestoes = []
        for produto_sugerido_id, vezes_comprado_junto in produtos_junto.items():
            frequencia = (
                Decimal(str(vezes_comprado_junto)) / Decimal(str(total_pedidos))
            ) * Decimal("100")

            # Filtra por frequência mínima (20%)
            if frequencia < Decimal("20"):
                continue

            # Determina prioridade baseado em frequência
            if frequencia >= Decimal("70"):
                prioridade = Priority.ALTA
            elif frequencia >= Decimal("40"):
                prioridade = Priority.MEDIA
            else:
                prioridade = Priority.BAIXA

            # Verifica se produto está ativo
            produto = (
                self.db.query(Produto)
                .filter(
                    Produto.tenant_id == tenant_id,  # Garantir isolamento multi-tenant
                    Produto.id == produto_sugerido_id,
                    Produto.ativo is True,
                )
                .first()
            )

            if not produto:
                continue

            explicacao = f"{frequencia:.0f}% dos clientes que compram este produto também compram {produto.nome}"

            sugestoes.append(
                ProductSuggestion(
                    produto_sugerido_id=produto_sugerido_id,
                    tipo=SuggestionType.COMPLEMENTAR,
                    frequencia=frequencia,
                    explicacao=explicacao,
                    prioridade=prioridade,
                )
            )

        # Ordena por frequência (maior primeiro)
        sugestoes.sort(key=lambda s: -s.frequencia)

        # Limita a 5 sugestões
        return sugestoes[:5]

    def get_substitute_products(
        self,
        tenant_id: UUID,
        produto_id: UUID,
        unavailable_product: UnavailableProduct,
    ) -> list[ProductSuggestion]:
        """
        Retorna produtos substitutos baseado em:
        - Mesma categoria (se houver)
        - Preço similar (±20%)
        """
        # Busca produto original
        produto_original = (
            self.db.query(Produto)
            .filter(Produto.id == produto_id, Produto.tenant_id == tenant_id)
            .first()
        )

        if not produto_original:
            return []

        # Busca produtos ativos similares (mesmo tenant, preço similar)
        preco_minimo = produto_original.preco_base * Decimal("0.8")
        preco_maximo = produto_original.preco_base * Decimal("1.2")

        produtos_similares = (
            self.db.query(Produto)
            .filter(
                Produto.tenant_id == tenant_id,
                Produto.id != produto_id,
                Produto.ativo is True,
                Produto.preco_base >= preco_minimo,
                Produto.preco_base <= preco_maximo,
            )
            .limit(5)
            .all()
        )

        sugestoes = []
        for produto in produtos_similares:
            diferenca_percentual = abs(
                (produto.preco_base - produto_original.preco_base) / produto_original.preco_base
            ) * Decimal("100")

            explicacao = (
                f"Produto similar: {produto.nome}. "
                f"Preço {'mais baixo' if produto.preco_base < produto_original.preco_base else 'mais alto'} "
                f"({diferenca_percentual:.0f}% de diferença)"
            )

            sugestoes.append(
                ProductSuggestion(
                    produto_sugerido_id=produto.id,
                    tipo=SuggestionType.SUBSTITUTO,
                    frequencia=Decimal("0"),  # Não há frequência para substitutos
                    explicacao=explicacao,
                    prioridade=Priority.MEDIA,
                    produto_original_id=produto_id,
                    motivo="preco_similar",
                )
            )

        return sugestoes

    def get_bundles(
        self,
        tenant_id: UUID,
        context: SuggestionContext | None = None,
    ) -> list[BundleSuggestion]:
        """
        Retorna bundles (combinações de produtos frequentemente vendidos juntos).
        Analisa pedidos entregues dos últimos 90 dias.
        """
        data_limite = datetime.utcnow() - timedelta(days=90)

        # Busca todos os pedidos entregues
        pedidos = (
            self.db.query(Pedido.id)
            .filter(
                Pedido.tenant_id == tenant_id,
                Pedido.status == "entregue",
                Pedido.entregue_em >= data_limite,
            )
            .all()
        )

        if not pedidos:
            return []

        # Agrupa produtos por pedido
        pedido_produtos = {}
        for pedido_id_tuple in pedidos:
            pedido_id = pedido_id_tuple[0]
            produtos = [
                item.produto_id
                for item in self.db.query(PedidoItem.produto_id)
                .filter(
                    PedidoItem.tenant_id == tenant_id,  # Garantir isolamento multi-tenant
                    PedidoItem.pedido_id == pedido_id,
                )
                .distinct()
                .all()
            ]
            if len(produtos) >= 2:  # Bundle precisa ter pelo menos 2 produtos
                pedido_produtos[pedido_id] = frozenset(produtos)

        # Conta frequência de combinações de 2-3 produtos
        combinacoes_frequentes = defaultdict(int)

        for produtos_set in pedido_produtos.values():
            produtos_list = list(produtos_set)
            # Combinações de 2 produtos
            for i in range(len(produtos_list)):
                for j in range(i + 1, len(produtos_list)):
                    combinacao = frozenset([produtos_list[i], produtos_list[j]])
                    combinacoes_frequentes[combinacao] += 1

        total_pedidos = len(pedido_produtos)
        if total_pedidos == 0:
            return []

        bundles = []
        from uuid import uuid4

        for combinacao, vezes in combinacoes_frequentes.items():
            frequencia = (Decimal(str(vezes)) / Decimal(str(total_pedidos))) * Decimal("100")

            # Filtra por frequência mínima (50%)
            if frequencia < Decimal("50"):
                continue

            produtos_list = list(combinacao)
            explicacao = f"Estes {len(produtos_list)} produtos são vendidos juntos em {frequencia:.0f}% das vendas"

            bundles.append(
                BundleSuggestion(
                    bundle_id=uuid4(),
                    produtos=produtos_list,
                    frequencia=frequencia,
                    explicacao=explicacao,
                    nome_bundle=None,
                )
            )

        # Ordena por frequência (maior primeiro)
        bundles.sort(key=lambda b: -b.frequencia)

        # Limita a 5 bundles
        return bundles[:5]

    def get_purchase_patterns(
        self,
        tenant_id: UUID,
        cliente_id: UUID | None = None,
    ) -> list[PurchasePattern]:
        """
        Retorna padrões de compra identificados.
        Analisa produtos frequentemente comprados juntos.
        """
        data_limite = datetime.utcnow() - timedelta(days=180)  # 6 meses

        # Busca pedidos entregues
        query = self.db.query(Pedido.id).filter(
            Pedido.tenant_id == tenant_id,
            Pedido.status == "entregue",
            Pedido.entregue_em >= data_limite,
        )

        if cliente_id:
            query = query.filter(Pedido.cliente_id == cliente_id)

        pedidos = query.all()

        if not pedidos:
            return []

        # Agrupa produtos por pedido
        pedido_produtos = {}
        for pedido_id_tuple in pedidos:
            pedido_id = pedido_id_tuple[0]
            produtos = [
                item.produto_id
                for item in self.db.query(PedidoItem.produto_id)
                .filter(
                    PedidoItem.tenant_id == tenant_id,  # Garantir isolamento multi-tenant
                    PedidoItem.pedido_id == pedido_id,
                )
                .distinct()
                .all()
            ]
            if len(produtos) >= 2:
                pedido_produtos[pedido_id] = frozenset(produtos)

        # Identifica padrões de 2-3 produtos
        padroes_frequentes = defaultdict(int)

        for produtos_set in pedido_produtos.values():
            produtos_list = list(produtos_set)
            # Padrões de 2 produtos
            for i in range(len(produtos_list)):
                for j in range(i + 1, min(i + 3, len(produtos_list))):
                    padrao = frozenset(produtos_list[i : j + 1])
                    if len(padrao) >= 2:
                        padroes_frequentes[padrao] += 1

        total_pedidos = len(pedido_produtos)
        if total_pedidos == 0:
            return []

        patterns = []
        from uuid import uuid4

        for padrao, vezes in padroes_frequentes.items():
            frequencia = (Decimal(str(vezes)) / Decimal(str(total_pedidos))) * Decimal("100")

            # Filtra por frequência mínima (30%)
            if frequencia < Decimal("30"):
                continue

            produtos_list = list(padrao)
            explicacao = f"Padrão: {frequencia:.0f}% dos pedidos contêm estes {len(produtos_list)} produtos juntos"

            contexto = f"por_cliente_{cliente_id}" if cliente_id else "geral"

            patterns.append(
                PurchasePattern(
                    padrao_id=uuid4(),
                    produtos=produtos_list,
                    frequencia=frequencia,
                    explicacao=explicacao,
                    contexto=contexto,
                )
            )

        # Ordena por frequência (maior primeiro)
        patterns.sort(key=lambda p: -p.frequencia)

        return patterns[:10]  # Top 10 padrões

    def register_sale(self, sale_event: SaleEvent) -> None:
        """
        Registra venda concluída.
        Nota: Histórico é calculado dinamicamente de PedidoItem com status="entregue",
        então não precisa armazenar separadamente. Este método serve para validação
        e possível cache futuro.
        """
        # Histórico é calculado dinamicamente de PedidoItem
        # Este método pode ser usado para validação ou cache futuro
        pass

    def record_suggestion_followed(self, feedback: SuggestionFollowed) -> None:
        """
        Registra feedback: sugestão foi seguida.
        Pode ser usado para melhorar algoritmos no futuro.
        """
        # Futuro: armazenar feedback para melhorar sugestões
        pass

    def record_suggestion_ignored(self, feedback: SuggestionIgnored) -> None:
        """
        Registra feedback: sugestão foi ignorada.
        Pode ser usado para melhorar algoritmos no futuro.
        """
        # Futuro: armazenar feedback para melhorar sugestões
        pass

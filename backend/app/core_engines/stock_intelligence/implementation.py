"""
Implementação real do Stock Intelligence Engine

Implementa lógica básica de análise de estoque e sugestões de reposição.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core_engines.stock_intelligence.dto import (
    ABCAnalysis,
    ProductClass,
    ReplenishmentParameters,
    ReplenishmentSuggestion,
    RiskLevel,
    SaleEvent,
    StockAlert,
    StockUpdate,
)
from app.core_engines.stock_intelligence.ports import StockIntelligencePort
from app.models.estoque import Estoque
from app.models.pedido import Pedido, PedidoItem
from app.models.produto import Produto


class StockIntelligenceImplementation(StockIntelligencePort):
    """
    Implementação real do Stock Intelligence Engine

    Usa dados do banco (PedidoItem com status="entregue" para histórico de vendas,
    Estoque para quantidade atual).
    """

    # Armazena parâmetros de reposição por produto (em memória - futuro: banco)
    _parameters: dict = {}

    def __init__(self, db: Session):
        self.db = db

    def get_stock_alerts(
        self,
        tenant_id: UUID,
        risk_level: str | None = None,
        product_ids: list[UUID] | None = None,
    ) -> list[StockAlert]:
        """
        Retorna alertas de risco de ruptura baseado em:
        - Estoque atual
        - Média de vendas históricas
        - Lead time configurado
        """
        alerts = []

        # Busca produtos ativos do tenant
        query = self.db.query(Produto).filter(Produto.tenant_id == tenant_id, Produto.ativo is True)

        if product_ids:
            query = query.filter(Produto.id.in_(product_ids))

        produtos = query.all()

        for produto in produtos:
            # Busca estoque atual
            estoque = (
                self.db.query(Estoque)
                .filter(Estoque.tenant_id == tenant_id, Estoque.produto_id == produto.id)
                .first()
            )

            quantidade_atual = estoque.quantidade_atual if estoque else Decimal("0")

            # Calcula média de vendas (últimos 90 dias)
            media_vendas = self._calcular_media_vendas(tenant_id, produto.id, dias=90)

            # Busca parâmetros de reposição
            params = self._get_parameters(tenant_id, produto.id)
            lead_time_dias = params.get("lead_time_dias", 7)
            estoque_seguranca_percentual = params.get("estoque_seguranca_percentual", Decimal("20"))

            # Calcula estoque mínimo sugerido
            estoque_minimo = self._calcular_estoque_minimo(
                media_vendas, lead_time_dias, estoque_seguranca_percentual
            )

            # Se estoque abaixo do mínimo, gera alerta
            if quantidade_atual < estoque_minimo:
                dias_ate_ruptura = None
                if media_vendas > 0:
                    dias_ate_ruptura = int((quantidade_atual / media_vendas).quantize(Decimal("1")))

                nivel_risco = self._determinar_nivel_risco(
                    quantidade_atual, estoque_minimo, dias_ate_ruptura
                )

                # Filtro por nível de risco se fornecido
                if risk_level and nivel_risco.value != risk_level:
                    continue

                explicacao = (
                    f"Estoque atual: {quantidade_atual}, "
                    f"Média de vendas: {media_vendas:.2f}/dia, "
                    f"Lead time: {lead_time_dias} dias, "
                    f"Estoque mínimo sugerido: {estoque_minimo:.2f}"
                )
                if dias_ate_ruptura is not None:
                    explicacao += f". Ruptura estimada em {dias_ate_ruptura} dias se não comprar."

                alerts.append(
                    StockAlert(
                        produto_id=produto.id,
                        tipo="ruptura",
                        nivel_risco=nivel_risco,
                        estoque_atual=quantidade_atual,
                        estoque_minimo_calculado=estoque_minimo,
                        dias_ate_ruptura=dias_ate_ruptura,
                        explicacao=explicacao,
                    )
                )

        # Ordena por nível de risco (alto primeiro)
        risk_order = {RiskLevel.ALTO: 0, RiskLevel.MEDIO: 1, RiskLevel.BAIXO: 2}
        alerts.sort(key=lambda a: risk_order.get(a.nivel_risco, 3))

        return alerts

    def get_replenishment_suggestions(
        self,
        tenant_id: UUID,
        product_ids: list[UUID] | None = None,
    ) -> list[ReplenishmentSuggestion]:
        """
        Retorna sugestões de reposição baseado em:
        - Estoque atual
        - Média de vendas históricas
        - Lead time e estoque de segurança
        """
        suggestions = []

        # Busca produtos ativos do tenant
        query = self.db.query(Produto).filter(Produto.tenant_id == tenant_id, Produto.ativo is True)

        if product_ids:
            query = query.filter(Produto.id.in_(product_ids))

        produtos = query.all()

        for produto in produtos:
            # Busca estoque atual
            estoque = (
                self.db.query(Estoque)
                .filter(Estoque.tenant_id == tenant_id, Estoque.produto_id == produto.id)
                .first()
            )

            quantidade_atual = estoque.quantidade_atual if estoque else Decimal("0")

            # Calcula média de vendas (últimos 90 dias)
            media_vendas = self._calcular_media_vendas(tenant_id, produto.id, dias=90)

            # Busca parâmetros de reposição
            params = self._get_parameters(tenant_id, produto.id)
            lead_time_dias = params.get("lead_time_dias", 7)
            estoque_seguranca_percentual = params.get("estoque_seguranca_percentual", Decimal("20"))

            # Calcula estoque mínimo e máximo
            estoque_minimo = self._calcular_estoque_minimo(
                media_vendas, lead_time_dias, estoque_seguranca_percentual
            )
            estoque_maximo = self._calcular_estoque_maximo(
                media_vendas, lead_time_dias, estoque_seguranca_percentual
            )

            # Se estoque abaixo do mínimo, sugere reposição
            if quantidade_atual < estoque_minimo:
                quantidade_sugerida = estoque_maximo - quantidade_atual
                if quantidade_sugerida < 0:
                    quantidade_sugerida = estoque_minimo

                # Determina prioridade baseado em análise ABC
                classe = self._calcular_classe_abc(tenant_id, produto.id)
                prioridade = (
                    "alta"
                    if classe == ProductClass.A
                    else ("media" if classe == ProductClass.B else "baixa")
                )

                explicacao = (
                    f"Vende {media_vendas:.2f} unidades/dia, lead time {lead_time_dias} dias. "
                    f"Sugestão: comprar {quantidade_sugerida:.2f} unidades para estoque máximo de {estoque_maximo:.2f}."
                )

                suggestions.append(
                    ReplenishmentSuggestion(
                        produto_id=produto.id,
                        quantidade_sugerida=quantidade_sugerida,
                        estoque_atual=quantidade_atual,
                        estoque_minimo_calculado=estoque_minimo,
                        estoque_maximo_sugerido=estoque_maximo,
                        prioridade=prioridade,
                        explicacao=explicacao,
                    )
                )

        # Ordena por prioridade
        priority_order = {"alta": 0, "media": 1, "baixa": 2}
        suggestions.sort(key=lambda s: priority_order.get(s.prioridade, 3))

        return suggestions

    def get_abc_analysis(
        self,
        tenant_id: UUID,
        product_ids: list[UUID] | None = None,
    ) -> list[ABCAnalysis]:
        """
        Retorna análise ABC baseado em histórico de vendas (análise de Pareto).
        Classe A: 20% dos produtos = 80% das vendas
        Classe B: 30% dos produtos = 15% das vendas
        Classe C: 50% dos produtos = 5% das vendas
        """
        # Busca produtos ativos do tenant
        query = self.db.query(Produto).filter(Produto.tenant_id == tenant_id, Produto.ativo is True)

        if product_ids:
            query = query.filter(Produto.id.in_(product_ids))

        produtos = query.all()

        # Calcula valor total vendido por produto (últimos 90 dias)
        produto_vendas = []
        for produto in produtos:
            valor_total = self._calcular_valor_total_vendido(tenant_id, produto.id, dias=90)
            produto_vendas.append(
                {
                    "produto_id": produto.id,
                    "valor_total": valor_total,
                }
            )

        # Ordena por valor total (maior primeiro)
        produto_vendas.sort(key=lambda x: x["valor_total"], reverse=True)

        # Calcula valor total de todas as vendas
        valor_total_geral = sum(pv["valor_total"] for pv in produto_vendas)

        if valor_total_geral == 0:
            # Se não há vendas, todos são classe C
            return [
                ABCAnalysis(
                    produto_id=pv["produto_id"],
                    classe=ProductClass.C,
                    percentual_vendas_acumulado=Decimal("0"),
                    percentual_produtos_acumulado=Decimal("100"),
                    explicacao="Sem vendas históricas",
                )
                for pv in produto_vendas
            ]

        # Classifica produtos em ABC
        acumulado_vendas = Decimal("0")
        acumulado_produtos = Decimal("0")
        total_produtos = len(produto_vendas)

        analyses = []

        for idx, pv in enumerate(produto_vendas):
            acumulado_vendas += pv["valor_total"]
            acumulado_produtos += Decimal("1")

            percentual_vendas_acumulado = (acumulado_vendas / valor_total_geral) * Decimal("100")
            percentual_produtos_acumulado = (acumulado_produtos / total_produtos) * Decimal("100")

            # Classifica baseado em percentual acumulado de vendas
            if percentual_vendas_acumulado <= Decimal("80"):
                classe = ProductClass.A
            elif percentual_vendas_acumulado <= Decimal("95"):
                classe = ProductClass.B
            else:
                classe = ProductClass.C

            explicacao = (
                f"Classe {classe.value}: {percentual_produtos_acumulado:.1f}% dos produtos = "
                f"{percentual_vendas_acumulado:.1f}% das vendas"
            )

            analyses.append(
                ABCAnalysis(
                    produto_id=pv["produto_id"],
                    classe=classe,
                    percentual_vendas_acumulado=percentual_vendas_acumulado,
                    percentual_produtos_acumulado=percentual_produtos_acumulado,
                    explicacao=explicacao,
                )
            )

        return analyses

    def register_sale(self, sale_event: SaleEvent) -> None:
        """
        Registra venda para atualizar histórico.
        Nota: Histórico é calculado dinamicamente de PedidoItem com status="entregue",
        então não precisa armazenar separadamente. Este método serve para validação
        e possível cache futuro.
        """
        # Histórico é calculado dinamicamente de PedidoItem
        # Este método pode ser usado para validação ou cache futuro
        pass

    def update_stock(self, stock_update: StockUpdate) -> None:
        """
        Atualiza estoque atual de um produto.
        Cria registro se não existe, atualiza se existe.
        """
        estoque = (
            self.db.query(Estoque)
            .filter(
                Estoque.tenant_id == stock_update.tenant_id,
                Estoque.produto_id == stock_update.produto_id,
            )
            .first()
        )

        if estoque:
            estoque.quantidade_atual = stock_update.quantidade_atual
            estoque.updated_at = stock_update.data_atualizacao
        else:
            estoque = Estoque(
                tenant_id=stock_update.tenant_id,
                produto_id=stock_update.produto_id,
                quantidade_atual=stock_update.quantidade_atual,
            )
            self.db.add(estoque)

        self.db.commit()

    def configure_replenishment_parameters(
        self,
        parameters: ReplenishmentParameters,
    ) -> None:
        """
        Configura parâmetros de reposição para um produto.
        Armazena em memória (futuro: banco de dados).
        """
        key = f"{parameters.tenant_id}_{parameters.produto_id}"
        self._parameters[key] = {
            "lead_time_dias": parameters.lead_time_dias,
            "estoque_seguranca_percentual": parameters.estoque_seguranca_percentual,
            "estoque_minimo_manual": parameters.estoque_minimo_manual,
            "estoque_maximo_manual": parameters.estoque_maximo_manual,
        }

    # Métodos auxiliares privados

    def _calcular_media_vendas(self, tenant_id: UUID, produto_id: UUID, dias: int = 90) -> Decimal:
        """Calcula média diária de vendas nos últimos N dias"""
        data_limite = datetime.utcnow() - timedelta(days=dias)

        # Soma quantidade vendida (PedidoItem de pedidos entregues)
        total_quantidade = self.db.query(func.sum(PedidoItem.quantidade)).join(
            Pedido, PedidoItem.pedido_id == Pedido.id
        ).filter(
            PedidoItem.tenant_id == tenant_id,
            PedidoItem.produto_id == produto_id,
            Pedido.status == "entregue",
            Pedido.entregue_em >= data_limite,
        ).scalar() or Decimal(
            "0"
        )

        # Calcula média diária
        if dias > 0:
            return total_quantidade / Decimal(str(dias))
        return Decimal("0")

    def _calcular_valor_total_vendido(
        self, tenant_id: UUID, produto_id: UUID, dias: int = 90
    ) -> Decimal:
        """Calcula valor total vendido nos últimos N dias"""
        data_limite = datetime.utcnow() - timedelta(days=dias)

        # Soma valor total vendido (PedidoItem de pedidos entregues)
        total_valor = self.db.query(func.sum(PedidoItem.valor_total)).join(
            Pedido, PedidoItem.pedido_id == Pedido.id
        ).filter(
            PedidoItem.tenant_id == tenant_id,
            PedidoItem.produto_id == produto_id,
            Pedido.status == "entregue",
            Pedido.entregue_em >= data_limite,
        ).scalar() or Decimal(
            "0"
        )

        return total_valor

    def _calcular_estoque_minimo(
        self,
        media_vendas: Decimal,
        lead_time_dias: int,
        estoque_seguranca_percentual: Decimal,
    ) -> Decimal:
        """
        Calcula estoque mínimo sugerido.
        Fórmula: (média de vendas * lead time) + (margem de segurança)
        """
        if media_vendas == 0:
            return Decimal("0")

        estoque_necessario = media_vendas * Decimal(str(lead_time_dias))
        margem_seguranca = estoque_necessario * (estoque_seguranca_percentual / Decimal("100"))

        return estoque_necessario + margem_seguranca

    def _calcular_estoque_maximo(
        self,
        media_vendas: Decimal,
        lead_time_dias: int,
        estoque_seguranca_percentual: Decimal,
    ) -> Decimal:
        """
        Calcula estoque máximo sugerido.
        Fórmula: (média de vendas * (lead time + período de cobertura)) + margem de segurança
        Período de cobertura: 30 dias (cobertura de 1 mês)
        """
        if media_vendas == 0:
            return Decimal("0")

        periodo_cobertura = 30  # dias
        estoque_necessario = media_vendas * Decimal(str(lead_time_dias + periodo_cobertura))
        margem_seguranca = estoque_necessario * (estoque_seguranca_percentual / Decimal("100"))

        return estoque_necessario + margem_seguranca

    def _determinar_nivel_risco(
        self,
        estoque_atual: Decimal,
        estoque_minimo: Decimal,
        dias_ate_ruptura: int | None,
    ) -> RiskLevel:
        """Determina nível de risco baseado em estoque atual e dias até ruptura"""
        if dias_ate_ruptura is None:
            return RiskLevel.BAIXO

        # Risco alto: ruptura em menos de 7 dias
        if dias_ate_ruptura <= 7:
            return RiskLevel.ALTO
        # Risco médio: ruptura em 7-14 dias
        elif dias_ate_ruptura <= 14:
            return RiskLevel.MEDIO
        # Risco baixo: ruptura em mais de 14 dias
        else:
            return RiskLevel.BAIXO

    def _calcular_classe_abc(self, tenant_id: UUID, produto_id: UUID) -> ProductClass:
        """Calcula classe ABC do produto"""
        # Busca análise ABC
        analyses = self.get_abc_analysis(tenant_id, product_ids=[produto_id])

        if analyses:
            return analyses[0].classe

        return ProductClass.C

    def _get_parameters(self, tenant_id: UUID, produto_id: UUID) -> dict:
        """Retorna parâmetros de reposição do produto"""
        key = f"{tenant_id}_{produto_id}"
        return self._parameters.get(
            key,
            {
                "lead_time_dias": 7,
                "estoque_seguranca_percentual": Decimal("20"),
                "estoque_minimo_manual": None,
                "estoque_maximo_manual": None,
            },
        )

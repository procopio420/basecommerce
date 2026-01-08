"""
Implementação real do Pricing & Supplier Intelligence Engine

Implementa lógica básica de comparação de fornecedores e cálculo de custo base.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core_engines.pricing_supplier.dto import (
    BaseCost,
    PriceTrend,
    PriceUpdate,
    PriceVariationAlert,
    SupplierComparison,
    SupplierComparisonItem,
    SupplierPrice,
    SupplierSuggestion,
)
from app.core_engines.pricing_supplier.ports import PricingSupplierIntelligencePort
from app.models.fornecedor import Fornecedor, FornecedorPreco
from app.models.produto import Produto


class PricingSupplierIntelligenceImplementation(PricingSupplierIntelligencePort):
    """
    Implementação real do Pricing & Supplier Intelligence Engine

    Usa dados do banco (FornecedorPreco para preços de fornecedores).
    Compara preços e calcula custo base.
    """

    # Threshold padrão para considerar variação relevante (10%)
    DEFAULT_VARIATION_THRESHOLD = Decimal("10")

    def __init__(self, db: Session):
        self.db = db

    def register_price(self, price: SupplierPrice) -> None:
        """
        Registra preço de fornecedor para um produto.
        Cria ou atualiza registro de preço.
        """
        # Busca fornecedor
        fornecedor = (
            self.db.query(Fornecedor)
            .filter(
                Fornecedor.tenant_id == price.tenant_id,
                Fornecedor.id == price.fornecedor_id,
                Fornecedor.ativo is True,
            )
            .first()
        )

        if not fornecedor:
            raise ValueError(f"Fornecedor {price.fornecedor_id} não encontrado")

        # Busca preço existente
        fornecedor_preco = (
            self.db.query(FornecedorPreco)
            .filter(
                FornecedorPreco.tenant_id == price.tenant_id,
                FornecedorPreco.fornecedor_id == price.fornecedor_id,
                FornecedorPreco.produto_id == price.produto_id,
                FornecedorPreco.valido is True,
            )
            .first()
        )

        if fornecedor_preco:
            # Marca preço antigo como inválido
            fornecedor_preco.valido = False
            self.db.flush()

            # Cria novo registro de preço (histórico)
            preco_anterior = fornecedor_preco.preco
            variacao_percentual = (
                abs((price.preco - preco_anterior) / preco_anterior) * Decimal("100")
                if preco_anterior > 0
                else Decimal("0")
            )

            # Gera alerta se variação significativa
            if variacao_percentual >= self.DEFAULT_VARIATION_THRESHOLD:
                # Alerta será gerado na próxima consulta
                pass

        # Cria novo registro de preço
        novo_preco = FornecedorPreco(
            tenant_id=price.tenant_id,
            fornecedor_id=price.fornecedor_id,
            produto_id=price.produto_id,
            preco=price.preco,
            quantidade_minima=price.condicoes.quantidade_minima if price.condicoes else None,
            prazo_pagamento=price.condicoes.prazo_pagamento if price.condicoes else None,
            valido=True,
        )

        self.db.add(novo_preco)
        self.db.commit()

    def update_price(self, price_update: PriceUpdate) -> None:
        """
        Atualiza preço de fornecedor.
        Marca preço antigo como inválido e cria novo registro.
        """
        # Marca preço antigo como inválido
        fornecedor_preco_antigo = (
            self.db.query(FornecedorPreco)
            .filter(
                FornecedorPreco.tenant_id == price_update.tenant_id,
                FornecedorPreco.fornecedor_id == price_update.fornecedor_id,
                FornecedorPreco.produto_id == price_update.produto_id,
                FornecedorPreco.valido is True,
            )
            .first()
        )

        if fornecedor_preco_antigo:
            fornecedor_preco_antigo.valido = False
            self.db.flush()

        # Cria novo registro de preço
        novo_preco = FornecedorPreco(
            tenant_id=price_update.tenant_id,
            fornecedor_id=price_update.fornecedor_id,
            produto_id=price_update.produto_id,
            preco=price_update.preco_novo,
            valido=True,
        )

        self.db.add(novo_preco)
        self.db.commit()

    def compare_suppliers(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> SupplierComparison:
        """
        Compara fornecedores para um produto.
        Retorna lista ordenada por preço (menor para maior).
        """
        # Busca todos os preços válidos do produto
        precos = (
            self.db.query(FornecedorPreco)
            .filter(
                FornecedorPreco.tenant_id == tenant_id,
                FornecedorPreco.produto_id == produto_id,
                FornecedorPreco.valido is True,
            )
            .all()
        )

        if not precos:
            return SupplierComparison(
                produto_id=produto_id,
                fornecedores=[],
            )

        # Ordena por preço (menor primeiro)
        precos_ordenados = sorted(precos, key=lambda p: p.preco)

        if not precos_ordenados:
            return SupplierComparison(
                produto_id=produto_id,
                fornecedores=[],
            )

        preco_mais_barato = precos_ordenados[0].preco

        # Calcula preço médio histórico (últimos 90 dias)
        data_limite = datetime.utcnow() - timedelta(days=90)

        fornecedores = []
        for preco in precos_ordenados:
            # Calcula preço médio histórico deste fornecedor
            precos_historicos = (
                self.db.query(FornecedorPreco.preco)
                .filter(
                    FornecedorPreco.tenant_id == tenant_id,
                    FornecedorPreco.fornecedor_id == preco.fornecedor_id,
                    FornecedorPreco.produto_id == produto_id,
                    FornecedorPreco.created_at >= data_limite,
                )
                .all()
            )

            if precos_historicos:
                precos_list = [p[0] for p in precos_historicos]
                preco_medio = sum(precos_list) / Decimal(str(len(precos_list)))
            else:
                preco_medio = None

            # Calcula variação vs mais barato
            if preco_mais_barato > 0:
                variacao = ((preco.preco - preco_mais_barato) / preco_mais_barato) * Decimal("100")
            else:
                variacao = Decimal("0")

            # Determina estabilidade (se preço médio próximo do atual, estável)
            if preco_medio:
                variacao_media = (
                    abs((preco.preco - preco_medio) / preco_medio) * Decimal("100")
                    if preco_medio > 0
                    else Decimal("0")
                )
                estabilidade = "estavel" if variacao_media < Decimal("5") else "instavel"
            else:
                estabilidade = "estavel"

            fornecedores.append(
                SupplierComparisonItem(
                    fornecedor_id=preco.fornecedor_id,
                    preco_atual=preco.preco,
                    variacao_vs_mais_barato=variacao,
                    preco_medio_historico=preco_medio,
                    estabilidade_preco=estabilidade,
                )
            )

        return SupplierComparison(
            produto_id=produto_id,
            fornecedores=fornecedores,
        )

    def suggest_supplier(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> SupplierSuggestion:
        """
        Sugere fornecedor mais vantajoso baseado em:
        - Preço atual (menor preço)
        - Estabilidade de preço (histórico)
        """
        # Compara fornecedores
        comparacao = self.compare_suppliers(tenant_id, produto_id)

        if not comparacao.fornecedores:
            raise ValueError(f"Nenhum fornecedor encontrado para produto {produto_id}")

        # Seleciona fornecedor mais barato que seja estável
        fornecedor_recomendado = None

        for fornecedor in comparacao.fornecedores:
            if fornecedor.estabilidade_preco == "estavel":
                fornecedor_recomendado = fornecedor
                break

        # Se não há fornecedor estável, usa o mais barato
        if not fornecedor_recomendado:
            fornecedor_recomendado = comparacao.fornecedores[0]

        # Custo base é o preço recomendado
        custo_base = fornecedor_recomendado.preco_atual

        # Alternativas são outros fornecedores com preços próximos (±5%)
        alternativas = []
        for fornecedor in comparacao.fornecedores:
            if fornecedor.fornecedor_id == fornecedor_recomendado.fornecedor_id:
                continue

            variacao_vs_recomendado = (
                abs((fornecedor.preco_atual - custo_base) / custo_base) * Decimal("100")
                if custo_base > 0
                else Decimal("100")
            )
            if variacao_vs_recomendado <= Decimal("5"):
                alternativas.append(fornecedor)

        explicacao = (
            f"Fornecedor {fornecedor_recomendado.fornecedor_id}: R$ {fornecedor_recomendado.preco_atual:.2f} "
            f"(mais barato{' e estável' if fornecedor_recomendado.estabilidade_preco == 'estavel' else ''})"
        )

        return SupplierSuggestion(
            produto_id=produto_id,
            fornecedor_recomendado_id=fornecedor_recomendado.fornecedor_id,
            preco_recomendado=fornecedor_recomendado.preco_atual,
            custo_base=custo_base,
            explicacao=explicacao,
            alternativas=alternativas[:3] if alternativas else None,
        )

    def get_base_cost(
        self,
        tenant_id: UUID,
        produto_id: UUID,
    ) -> BaseCost:
        """
        Retorna custo base de um produto (preço do fornecedor recomendado ou preço médio).
        """
        try:
            # Tenta obter sugestão de fornecedor
            sugestao = self.suggest_supplier(tenant_id, produto_id)

            return BaseCost(
                produto_id=produto_id,
                custo_base=sugestao.custo_base,
                fornecedor_usado_id=sugestao.fornecedor_recomendado_id,
                data_ultima_atualizacao=datetime.utcnow(),
            )
        except ValueError:
            # Se não há fornecedores, usa preço base do produto como fallback
            produto = (
                self.db.query(Produto)
                .filter(Produto.tenant_id == tenant_id, Produto.id == produto_id)
                .first()
            )

            if not produto:
                raise ValueError(f"Produto {produto_id} não encontrado")

            return BaseCost(
                produto_id=produto_id,
                custo_base=produto.preco_base,
                fornecedor_usado_id=None,
                data_ultima_atualizacao=datetime.utcnow(),
            )

    def get_price_alerts(
        self,
        tenant_id: UUID,
        produto_id: UUID | None = None,
    ) -> list[PriceVariationAlert]:
        """
        Retorna alertas de variação de preço significativa.
        Analisa mudanças nos últimos 30 dias.
        """
        data_limite = datetime.utcnow() - timedelta(days=30)

        # Busca todos os preços criados nos últimos 30 dias
        query = self.db.query(FornecedorPreco).filter(
            FornecedorPreco.tenant_id == tenant_id,
            FornecedorPreco.created_at >= data_limite,
            FornecedorPreco.valido is True,
        )

        if produto_id:
            query = query.filter(FornecedorPreco.produto_id == produto_id)

        precos_recentes = query.all()

        alerts = []

        for preco_atual in precos_recentes:
            # Busca preço anterior válido deste fornecedor para este produto
            preco_anterior = (
                self.db.query(FornecedorPreco)
                .filter(
                    FornecedorPreco.tenant_id == tenant_id,
                    FornecedorPreco.fornecedor_id == preco_atual.fornecedor_id,
                    FornecedorPreco.produto_id == preco_atual.produto_id,
                    FornecedorPreco.valido is False,
                    FornecedorPreco.created_at < preco_atual.created_at,
                )
                .order_by(FornecedorPreco.created_at.desc())
                .first()
            )

            if not preco_anterior:
                continue

            # Calcula variação percentual
            if preco_anterior.preco > 0:
                variacao = (
                    (preco_atual.preco - preco_anterior.preco) / preco_anterior.preco
                ) * Decimal("100")
            else:
                continue

            # Se variação >= threshold, gera alerta
            if abs(variacao) >= self.DEFAULT_VARIATION_THRESHOLD:
                tipo_alerta = "aumento" if variacao > 0 else "diminuicao"

                explicacao = (
                    f"Preço {'aumentou' if tipo_alerta == 'aumento' else 'diminuiu'} "
                    f"{abs(variacao):.1f}% em relação ao preço anterior "
                    f"(R$ {preco_anterior.preco:.2f} → R$ {preco_atual.preco:.2f})"
                )

                alerts.append(
                    PriceVariationAlert(
                        produto_id=preco_atual.produto_id,
                        fornecedor_id=preco_atual.fornecedor_id,
                        preco_anterior=preco_anterior.preco,
                        preco_atual=preco_atual.preco,
                        variacao_percentual=variacao,
                        tipo_alerta=tipo_alerta,
                        explicacao=explicacao,
                    )
                )

        # Ordena por variação (maior variação primeiro)
        alerts.sort(key=lambda a: abs(a.variacao_percentual), reverse=True)

        return alerts

    def get_price_trend(
        self,
        tenant_id: UUID,
        produto_id: UUID,
        fornecedor_id: UUID,
    ) -> PriceTrend:
        """
        Retorna tendência de preço ao longo do tempo.
        Analisa histórico dos últimos 90 dias.
        """
        data_limite = datetime.utcnow() - timedelta(days=90)

        # Busca histórico de preços
        precos_historicos = (
            self.db.query(FornecedorPreco.preco, FornecedorPreco.created_at)
            .filter(
                FornecedorPreco.tenant_id == tenant_id,
                FornecedorPreco.fornecedor_id == fornecedor_id,
                FornecedorPreco.produto_id == produto_id,
                FornecedorPreco.created_at >= data_limite,
            )
            .order_by(FornecedorPreco.created_at)
            .all()
        )

        if len(precos_historicos) < 2:
            # Sem histórico suficiente
            return PriceTrend(
                produto_id=produto_id,
                fornecedor_id=fornecedor_id,
                tendencia="estavel",
                variacao_percentual_periodo=Decimal("0"),
            )

        preco_inicial = precos_historicos[0][0]
        preco_final = precos_historicos[-1][0]

        # Calcula variação percentual no período
        if preco_inicial > 0:
            variacao_percentual = ((preco_final - preco_inicial) / preco_inicial) * Decimal("100")
        else:
            variacao_percentual = Decimal("0")

        # Determina tendência
        if abs(variacao_percentual) < Decimal("2"):  # Variação < 2% = estável
            tendencia = "estavel"
        elif variacao_percentual > 0:
            tendencia = "aumento"
        else:
            tendencia = "diminuicao"

        # Calcula previsão simples (variação mensal)
        dias_periodo = (precos_historicos[-1][1] - precos_historicos[0][1]).days
        if dias_periodo > 0:
            variacao_mensal = (variacao_percentual / Decimal(str(dias_periodo))) * Decimal("30")
            previsao = f"Tendência de {tendencia}: {variacao_mensal:+.1f}% ao mês"
        else:
            previsao = None

        return PriceTrend(
            produto_id=produto_id,
            fornecedor_id=fornecedor_id,
            tendencia=tendencia,
            variacao_percentual_periodo=variacao_percentual,
            previsao_simples=previsao,
        )

"""
Endpoints para Pricing & Supplier Intelligence Engine

Expõe funcionalidades de comparação de fornecedores e análise de preços.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_tenant_id, require_admin_role
from app.core_engines.pricing_supplier import PricingSupplierIntelligenceImplementation
from app.core_engines.pricing_supplier.dto import (
    PriceConditions,
    SupplierPrice,
)
from app.models.user import User

router = APIRouter()


# Schemas de Request/Response
class PriceConditionsRequest(BaseModel):
    quantidade_minima: float | None = None
    prazo_pagamento: int | None = None
    validade_preco: str | None = None


class SupplierPriceRequest(BaseModel):
    fornecedor_id: UUID
    produto_id: UUID
    preco: float = Field(..., gt=0)
    condicoes: PriceConditionsRequest | None = None


class SupplierComparisonItemResponse(BaseModel):
    fornecedor_id: UUID
    preco_atual: float
    variacao_vs_mais_barato: float
    preco_medio_historico: float | None = None
    estabilidade_preco: str

    class Config:
        from_attributes = True


class SupplierComparisonResponse(BaseModel):
    produto_id: UUID
    fornecedores: list[SupplierComparisonItemResponse]

    class Config:
        from_attributes = True


class SupplierSuggestionResponse(BaseModel):
    produto_id: UUID
    fornecedor_recomendado_id: UUID
    preco_recomendado: float
    custo_base: float
    explicacao: str
    alternativas: list[SupplierComparisonItemResponse] | None = None

    class Config:
        from_attributes = True


class BaseCostResponse(BaseModel):
    produto_id: UUID
    custo_base: float
    fornecedor_usado_id: UUID | None = None
    data_ultima_atualizacao: str | None = None

    class Config:
        from_attributes = True


class PriceVariationAlertResponse(BaseModel):
    produto_id: UUID
    fornecedor_id: UUID
    preco_anterior: float
    preco_atual: float
    variacao_percentual: float
    tipo_alerta: str
    explicacao: str

    class Config:
        from_attributes = True


class PriceTrendResponse(BaseModel):
    produto_id: UUID
    fornecedor_id: UUID
    tendencia: str
    variacao_percentual_periodo: float
    previsao_simples: str | None = None

    class Config:
        from_attributes = True


@router.post("/register-price", status_code=status.HTTP_204_NO_CONTENT)
async def register_price(
    request: SupplierPriceRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Registra preço de fornecedor para um produto.
    """
    try:
        from datetime import datetime
        from decimal import Decimal

        tenant_uuid = UUID(tenant_id)
        engine = PricingSupplierIntelligenceImplementation(db)

        conditions = None
        if request.condicoes:
            validade_preco = None
            if request.condicoes.validade_preco:
                validade_preco = datetime.fromisoformat(
                    request.condicoes.validade_preco.replace("Z", "+00:00")
                )

            conditions = PriceConditions(
                quantidade_minima=Decimal(str(request.condicoes.quantidade_minima))
                if request.condicoes.quantidade_minima is not None
                else None,
                prazo_pagamento=request.condicoes.prazo_pagamento,
                validade_preco=validade_preco,
            )

        price = SupplierPrice(
            tenant_id=tenant_uuid,
            produto_id=request.produto_id,
            fornecedor_id=request.fornecedor_id,
            preco=Decimal(str(request.preco)),
            unidade="UN",  # Padrão, pode ser configurado no futuro
            data_preco=datetime.utcnow(),
            condicoes=conditions,
        )

        engine.register_price(price)

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/compare/{produto_id}", response_model=SupplierComparisonResponse)
async def compare_suppliers(
    produto_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Compara fornecedores para um produto.
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = PricingSupplierIntelligenceImplementation(db)

        comparison = engine.compare_suppliers(tenant_uuid, produto_id)

        return comparison
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/suggest/{produto_id}", response_model=SupplierSuggestionResponse)
async def suggest_supplier(
    produto_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Sugere fornecedor mais vantajoso para um produto.
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = PricingSupplierIntelligenceImplementation(db)

        suggestion = engine.suggest_supplier(tenant_uuid, produto_id)

        return suggestion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/base-cost/{produto_id}", response_model=BaseCostResponse)
async def get_base_cost(
    produto_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna custo base de um produto.
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = PricingSupplierIntelligenceImplementation(db)

        base_cost = engine.get_base_cost(tenant_uuid, produto_id)

        return base_cost
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/price-alerts", response_model=list[PriceVariationAlertResponse])
async def get_price_alerts(
    produto_id: UUID | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna alertas de variação de preço significativa.
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = PricingSupplierIntelligenceImplementation(db)

        alerts = engine.get_price_alerts(tenant_uuid, produto_id)

        return alerts
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/price-trend/{produto_id}/{fornecedor_id}", response_model=PriceTrendResponse)
async def get_price_trend(
    produto_id: UUID,
    fornecedor_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna tendência de preço ao longo do tempo.
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = PricingSupplierIntelligenceImplementation(db)

        trend = engine.get_price_trend(tenant_uuid, produto_id, fornecedor_id)

        return trend
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

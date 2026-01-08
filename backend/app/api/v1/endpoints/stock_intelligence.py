"""
Endpoints para Stock Intelligence Engine

Expõe funcionalidades de análise de estoque e sugestões de reposição.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_tenant_id, require_admin_role
from app.core_engines.stock_intelligence import StockIntelligenceImplementation
from app.core_engines.stock_intelligence.dto import (
    ReplenishmentParameters,
    StockUpdate,
)
from app.models.user import User

router = APIRouter()


# Schemas de Request/Response
class StockUpdateRequest(BaseModel):
    produto_id: UUID
    quantidade_atual: float = Field(..., gt=0)
    tipo_movimento: str = Field(..., pattern="^(entrada|saida|ajuste)$")


class ReplenishmentParametersRequest(BaseModel):
    produto_id: UUID
    lead_time_dias: int = Field(..., gt=0)
    estoque_seguranca_percentual: float = Field(..., ge=0, le=100)
    estoque_minimo_manual: float | None = None
    estoque_maximo_manual: float | None = None


class StockAlertResponse(BaseModel):
    produto_id: UUID
    tipo: str
    nivel_risco: str
    estoque_atual: float
    estoque_minimo_calculado: float
    dias_ate_ruptura: int | None
    explicacao: str

    class Config:
        from_attributes = True


class ReplenishmentSuggestionResponse(BaseModel):
    produto_id: UUID
    quantidade_sugerida: float
    estoque_atual: float
    estoque_minimo_calculado: float
    estoque_maximo_sugerido: float
    prioridade: str
    explicacao: str

    class Config:
        from_attributes = True


class ABCAnalysisResponse(BaseModel):
    produto_id: UUID
    classe: str
    percentual_vendas_acumulado: float
    percentual_produtos_acumulado: float
    explicacao: str

    class Config:
        from_attributes = True


@router.get("/alerts", response_model=list[StockAlertResponse])
async def get_stock_alerts(
    risk_level: str | None = None,
    produto_id: UUID | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna alertas de risco de ruptura ou excesso de estoque.

    - **risk_level**: Filtro opcional por nível de risco ("alto", "medio", "baixo")
    - **produto_id**: Filtro opcional por produto específico
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = StockIntelligenceImplementation(db)

        product_ids = [produto_id] if produto_id else None

        alerts = engine.get_stock_alerts(
            tenant_id=tenant_uuid,
            risk_level=risk_level,
            product_ids=product_ids,
        )

        return alerts
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/suggestions", response_model=list[ReplenishmentSuggestionResponse])
async def get_replenishment_suggestions(
    produto_id: UUID | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna sugestões de reposição de estoque.

    - **produto_id**: Filtro opcional por produto específico
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = StockIntelligenceImplementation(db)

        product_ids = [produto_id] if produto_id else None

        suggestions = engine.get_replenishment_suggestions(
            tenant_id=tenant_uuid,
            product_ids=product_ids,
        )

        return suggestions
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/abc-analysis", response_model=list[ABCAnalysisResponse])
async def get_abc_analysis(
    produto_id: UUID | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna análise ABC (classificação de produtos por importância).

    - **produto_id**: Filtro opcional por produto específico
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = StockIntelligenceImplementation(db)

        product_ids = [produto_id] if produto_id else None

        analysis = engine.get_abc_analysis(
            tenant_id=tenant_uuid,
            product_ids=product_ids,
        )

        return analysis
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/update-stock", status_code=status.HTTP_204_NO_CONTENT)
async def update_stock(
    request: StockUpdateRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Atualiza estoque atual de um produto.
    """
    try:
        from datetime import datetime
        from decimal import Decimal

        tenant_uuid = UUID(tenant_id)
        engine = StockIntelligenceImplementation(db)

        stock_update = StockUpdate(
            tenant_id=tenant_uuid,
            produto_id=request.produto_id,
            quantidade_atual=Decimal(str(request.quantidade_atual)),
            data_atualizacao=datetime.utcnow(),
            tipo_movimento=request.tipo_movimento,
        )

        engine.update_stock(stock_update)

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/configure-parameters", status_code=status.HTTP_204_NO_CONTENT)
async def configure_replenishment_parameters(
    request: ReplenishmentParametersRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Configura parâmetros de reposição para um produto.
    """
    try:
        from decimal import Decimal

        tenant_uuid = UUID(tenant_id)
        engine = StockIntelligenceImplementation(db)

        parameters = ReplenishmentParameters(
            tenant_id=tenant_uuid,
            produto_id=request.produto_id,
            lead_time_dias=request.lead_time_dias,
            estoque_seguranca_percentual=Decimal(str(request.estoque_seguranca_percentual)),
            estoque_minimo_manual=Decimal(str(request.estoque_minimo_manual))
            if request.estoque_minimo_manual
            else None,
            estoque_maximo_manual=Decimal(str(request.estoque_maximo_manual))
            if request.estoque_maximo_manual
            else None,
        )

        engine.configure_replenishment_parameters(parameters)

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

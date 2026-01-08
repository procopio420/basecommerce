"""
Endpoints para Sales Intelligence Engine

Expõe funcionalidades de sugestões de produtos e análise de padrões de compra.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_tenant_id, require_admin_role
from app.core_engines.sales_intelligence import SalesIntelligenceImplementation
from app.core_engines.sales_intelligence.dto import (
    CartProduct,
    SuggestionContext,
)
from app.models.user import User

router = APIRouter()


# Schemas de Request/Response
class CartProductRequest(BaseModel):
    produto_id: UUID
    quantidade: float = Field(..., gt=0)


class SuggestionContextRequest(BaseModel):
    contexto: str = Field(..., pattern="^(criando_cotacao|finalizando_pedido)$")
    cliente_id: UUID | None = None
    produtos_carrinho: list[CartProductRequest] | None = None
    categoria_contexto: str | None = None


class ProductSuggestionResponse(BaseModel):
    produto_sugerido_id: UUID
    tipo: str
    frequencia: float
    explicacao: str
    prioridade: str
    produto_original_id: UUID | None = None
    motivo: str | None = None

    class Config:
        from_attributes = True


class BundleSuggestionResponse(BaseModel):
    bundle_id: UUID
    nome_bundle: str | None = None
    produtos: list[UUID]
    frequencia: float
    desconto_sugerido: float | None = None
    explicacao: str

    class Config:
        from_attributes = True


class PurchasePatternResponse(BaseModel):
    padrao_id: UUID
    produtos: list[UUID]
    frequencia: float
    contexto: str | None = None
    explicacao: str

    class Config:
        from_attributes = True


@router.post("/suggestions", response_model=list[ProductSuggestionResponse])
async def get_suggestions(
    request: SuggestionContextRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna sugestões de produtos baseadas no contexto atual.
    """
    try:
        from decimal import Decimal

        tenant_uuid = UUID(tenant_id)
        engine = SalesIntelligenceImplementation(db)

        produtos_carrinho = None
        if request.produtos_carrinho:
            produtos_carrinho = [
                CartProduct(
                    produto_id=p.produto_id,
                    quantidade=Decimal(str(p.quantidade)),
                )
                for p in request.produtos_carrinho
            ]

        context = SuggestionContext(
            tenant_id=tenant_uuid,
            contexto=request.contexto,
            cliente_id=request.cliente_id,
            produtos_carrinho=produtos_carrinho or [],
            categoria_contexto=request.categoria_contexto,
        )

        suggestions = engine.get_suggestions(context)

        return suggestions
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/complementary/{produto_id}", response_model=list[ProductSuggestionResponse])
async def get_complementary_products(
    produto_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna produtos complementares de um produto.
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = SalesIntelligenceImplementation(db)

        suggestions = engine.get_complementary_products(tenant_uuid, produto_id)

        return suggestions
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/bundles", response_model=list[BundleSuggestionResponse])
async def get_bundles(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna bundles (pacotes de produtos) sugeridos.
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = SalesIntelligenceImplementation(db)

        bundles = engine.get_bundles(tenant_uuid)

        return bundles
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/patterns", response_model=list[PurchasePatternResponse])
async def get_purchase_patterns(
    cliente_id: UUID | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna padrões de compra identificados.

    - **cliente_id**: Filtro opcional por cliente específico
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = SalesIntelligenceImplementation(db)

        patterns = engine.get_purchase_patterns(tenant_uuid, cliente_id)

        return patterns
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

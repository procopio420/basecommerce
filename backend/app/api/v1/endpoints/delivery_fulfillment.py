"""
Endpoints para Delivery & Fulfillment Engine

Expõe funcionalidades de planejamento de rotas e controle de entregas.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_tenant_id, require_admin_role
from app.core_engines.delivery_fulfillment import DeliveryFulfillmentImplementation
from app.core_engines.delivery_fulfillment.dto import (
    DeliveryAddress,
    DeliveryProduct,
    DeliveryStatus,
    DeliveryStatusUpdate,
    ReadyForDeliveryOrder,
)
from app.models.user import User

router = APIRouter()


# Schemas de Request/Response
class GPSLocationRequest(BaseModel):
    latitude: float
    longitude: float


class DeliveryAddressRequest(BaseModel):
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str
    coordenadas_gps: GPSLocationRequest | None = None
    instrucoes_acesso: str | None = None
    horario_preferencial: str | None = None


class DeliveryProductRequest(BaseModel):
    produto_id: UUID
    quantidade: float = Field(..., gt=0)
    peso: float | None = None
    volume: float | None = None


class ReadyForDeliveryOrderRequest(BaseModel):
    pedido_id: UUID
    cliente_id: UUID
    endereco_entrega: DeliveryAddressRequest
    produtos: list[DeliveryProductRequest]
    obra_id: UUID | None = None
    prioridade: str = Field(default="normal", pattern="^(alta|normal|baixa)$")
    observacoes: str | None = None


class RouteItemResponse(BaseModel):
    pedido_id: UUID
    ordem: int
    endereco: DeliveryAddressRequest
    distancia_estimada: float | None = None

    class Config:
        from_attributes = True


class DeliveryRouteResponse(BaseModel):
    rota_id: UUID
    pedidos: list[RouteItemResponse]
    motorista_sugerido_id: UUID | None = None
    veiculo_sugerido_id: UUID | None = None
    distancia_total_estimada: float | None = None
    tempo_total_estimado: int | None = None

    class Config:
        from_attributes = True


class DeliveryStatusUpdateRequest(BaseModel):
    delivery_id: UUID
    pedido_id: UUID
    status_novo: str = Field(
        ..., pattern="^(pendente|em_preparacao|saiu_entrega|chegou|entregue|cancelado)$"
    )
    motorista_id: UUID | None = None
    observacoes: str | None = None


@router.post("/plan-routes", response_model=list[DeliveryRouteResponse])
async def plan_routes(
    orders: list[ReadyForDeliveryOrderRequest],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Planeja rotas agrupando pedidos por região.
    """
    try:
        from decimal import Decimal

        tenant_uuid = UUID(tenant_id)
        engine = DeliveryFulfillmentImplementation(db)

        # Converte requests para DTOs
        ready_orders = []
        for order in orders:
            # Converte endereço
            gps_location = None
            if order.endereco_entrega.coordenadas_gps:
                from app.core_engines.delivery_fulfillment.dto import GPSLocation

                gps_location = GPSLocation(
                    latitude=Decimal(str(order.endereco_entrega.coordenadas_gps.latitude)),
                    longitude=Decimal(str(order.endereco_entrega.coordenadas_gps.longitude)),
                )

            endereco = DeliveryAddress(
                rua=order.endereco_entrega.rua,
                numero=order.endereco_entrega.numero,
                bairro=order.endereco_entrega.bairro,
                cidade=order.endereco_entrega.cidade,
                estado=order.endereco_entrega.estado,
                cep=order.endereco_entrega.cep,
                coordenadas_gps=gps_location,
                instrucoes_acesso=order.endereco_entrega.instrucoes_acesso,
                horario_preferencial=order.endereco_entrega.horario_preferencial,
            )

            # Converte produtos
            produtos = [
                DeliveryProduct(
                    produto_id=p.produto_id,
                    quantidade=Decimal(str(p.quantidade)),
                    peso=Decimal(str(p.peso)) if p.peso else None,
                    volume=Decimal(str(p.volume)) if p.volume else None,
                )
                for p in order.produtos
            ]

            ready_order = ReadyForDeliveryOrder(
                tenant_id=tenant_uuid,
                pedido_id=order.pedido_id,
                cliente_id=order.cliente_id,
                endereco_entrega=endereco,
                produtos=produtos,
                obra_id=order.obra_id,
                prioridade=order.prioridade,
                observacoes=order.observacoes,
            )

            ready_orders.append(ready_order)

        routes = engine.plan_routes(ready_orders)

        return routes
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/update-status", status_code=status.HTTP_204_NO_CONTENT)
async def update_delivery_status(
    request: DeliveryStatusUpdateRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Atualiza status da entrega.
    """
    try:
        from datetime import datetime

        tenant_uuid = UUID(tenant_id)
        engine = DeliveryFulfillmentImplementation(db)

        # Busca status anterior
        status_anterior = engine.get_delivery_status(tenant_uuid, request.pedido_id)

        status_update = DeliveryStatusUpdate(
            tenant_id=tenant_uuid,
            delivery_id=request.delivery_id,
            pedido_id=request.pedido_id,
            status_anterior=status_anterior,
            status_novo=DeliveryStatus(request.status_novo),
            motorista_id=request.motorista_id,
            timestamp=datetime.utcnow(),
            observacoes=request.observacoes,
        )

        engine.update_delivery_status(status_update)

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/status/{pedido_id}")
async def get_delivery_status(
    pedido_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role),
):
    """
    Retorna status atual da entrega.
    """
    try:
        tenant_uuid = UUID(tenant_id)
        engine = DeliveryFulfillmentImplementation(db)

        status_delivery = engine.get_delivery_status(tenant_uuid, pedido_id)

        return {"status": status_delivery.value}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

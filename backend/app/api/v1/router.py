from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    clientes,
    cotacoes,
    dashboard,
    delivery_fulfillment,
    obras,
    pedidos,
    pricing_supplier,
    produtos,
    sales_intelligence,
    stock_intelligence,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(obras.router, prefix="/obras", tags=["obras"])
api_router.include_router(produtos.router, prefix="/produtos", tags=["produtos"])
api_router.include_router(cotacoes.router, prefix="/cotacoes", tags=["cotacoes"])
api_router.include_router(pedidos.router, prefix="/pedidos", tags=["pedidos"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Core Engines Endpoints
api_router.include_router(
    stock_intelligence.router, prefix="/engines/stock", tags=["Stock Intelligence"]
)
api_router.include_router(
    sales_intelligence.router, prefix="/engines/sales", tags=["Sales Intelligence"]
)
api_router.include_router(
    pricing_supplier.router, prefix="/engines/pricing", tags=["Pricing & Supplier Intelligence"]
)
api_router.include_router(
    delivery_fulfillment.router, prefix="/engines/delivery", tags=["Delivery & Fulfillment"]
)

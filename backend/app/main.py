from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

# Configurar logging antes de criar app
setup_logging()

app = FastAPI(
    title="Construção SaaS API",
    description="API para gestão de cotações e pedidos em lojas de materiais de construção",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Construção SaaS API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

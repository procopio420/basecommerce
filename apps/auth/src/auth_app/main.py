"""
Auth Service - Standalone authentication microservice.

This service is a placeholder for future auth service expansion.
Currently, authentication is handled within each vertical.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from basecore.logging import setup_logging
from basecore.settings import get_settings

setup_logging()
settings = get_settings()

app = FastAPI(
    title="Auth Service",
    description="Authentication service for BaseCommerce platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Auth Service", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

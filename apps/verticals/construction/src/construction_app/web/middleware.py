"""Tenant resolution middleware for subdomain-based multi-tenancy.

The middleware extracts tenant slug from X-Tenant-Slug header (set by Nginx).
Tenant/branding details are fetched by the frontend via /tenant.json (auth service).
"""

import logging
import re
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


def get_tenant_slug_from_request(request: Request) -> Optional[str]:
    """
    Extract tenant slug from request.
    
    Priority:
    1. X-Tenant-Slug header (injected by Nginx in production)
    2. Parse from Host header (fallback for local development)
    
    Examples:
    - Header "X-Tenant-Slug: acme" -> "acme"
    - Host "acme.basecommerce.com.br" -> "acme"
    - Host "acme.localhost:8000" -> "acme"
    - Host "localhost:8000" -> None (development mode without tenant)
    """
    # Priority 1: X-Tenant-Slug header (set by Nginx)
    tenant_slug = request.headers.get("x-tenant-slug", "").strip()
    if tenant_slug:
        return tenant_slug
    
    # Priority 2: Parse from Host header (local development fallback)
    host = request.headers.get("host", "")
    return extract_slug_from_host(host)


def extract_slug_from_host(host: str) -> Optional[str]:
    """
    Extract tenant slug from Host header.
    
    Examples:
    - "acme.basecommerce.com.br" -> "acme"
    - "acme.basecommerce.com.br:8000" -> "acme"
    - "acme.localhost:8000" -> "acme"
    - "localhost:8000" -> None (development mode)
    - "basecommerce.com.br" -> None (root domain)
    """
    # Remove port if present
    host = host.split(":")[0].lower()
    
    # Development mode: localhost or IP addresses
    if host in ("localhost", "127.0.0.1") or re.match(r"^\d+\.\d+\.\d+\.\d+$", host):
        return None
    
    # Check for subdomain pattern: slug.basecommerce.com.br
    # Also support slug.localhost for local development with /etc/hosts
    parts = host.split(".")
    
    # Pattern: slug.domain.tld (at least 3 parts for production)
    # Or: slug.localhost (2 parts for local dev)
    if len(parts) >= 3:
        # e.g., acme.basecommerce.com.br -> acme
        return parts[0]
    elif len(parts) == 2 and parts[1] == "localhost":
        # e.g., acme.localhost -> acme
        return parts[0]
    
    return None


class TenantResolutionMiddleware(BaseHTTPMiddleware):
    """
    Middleware that resolves tenant slug from X-Tenant-Slug header or Host header.
    
    In production, Nginx injects the X-Tenant-Slug header based on subdomain.
    In development, the middleware parses the Host header directly.
    
    Note: Tenant details (branding, features) are fetched via /tenant.json
    which is served by the auth service. This middleware only extracts the slug.
    
    Sets request.state attributes:
    - tenant_slug: slug extracted from header/host
    """

    # Paths that don't require tenant resolution
    EXCLUDED_PATHS = (
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/auth/",  # API auth uses token-based tenant
    )

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip tenant resolution for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS):
            return await call_next(request)
        
        # Skip for API routes (they use token-based tenant resolution)
        if path.startswith("/api/"):
            return await call_next(request)
        
        # Get tenant slug from header or host
        slug = get_tenant_slug_from_request(request)
        
        # Set tenant slug in request state
        request.state.tenant_slug = slug
        
        if slug:
            logger.debug(f"Tenant slug resolved: {slug}")
        
        response = await call_next(request)
        return response


class DefaultBranding:
    """Default branding when no tenant-specific branding exists."""
    
    logo_url: Optional[str] = None
    primary_color: str = "#1a73e8"
    secondary_color: str = "#ea4335"
    feature_flags: dict = {}

    def __init__(self):
        self.feature_flags = {}

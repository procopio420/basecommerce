from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


# =============================================================================
# Login Schemas
# =============================================================================


class LoginRequest(BaseModel):
    """Request body for JSON login."""

    email: EmailStr
    password: str
    tenant_slug: Optional[str] = None  # Optional if using subdomain


class TokenResponse(BaseModel):
    """Response for successful login."""

    access_token: str
    token_type: str = "bearer"


# =============================================================================
# User Schemas
# =============================================================================


class UserResponse(BaseModel):
    """Response for /me endpoint."""

    id: UUID
    tenant_id: UUID
    nome: str
    email: str
    role: str
    ativo: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Request schema for creating a new user."""

    nome: str
    email: EmailStr
    password: Optional[str] = None  # Optional - if None, generates automatically
    role: str = "vendedor"  # admin or vendedor


class UserCreatedResponse(BaseModel):
    """Response schema for user creation."""

    id: UUID
    tenant_id: UUID
    nome: str
    email: str
    role: str
    ativo: bool
    password: Optional[str] = None  # Only present if password was auto-generated

    class Config:
        from_attributes = True


# =============================================================================
# Tenant Schemas
# =============================================================================


class TenantBrandingResponse(BaseModel):
    """Branding information for a tenant."""

    logo_url: Optional[str] = None
    primary_color: str = "#1a73e8"
    secondary_color: str = "#ea4335"
    feature_flags: dict = {}

    class Config:
        from_attributes = True


class TenantResponse(BaseModel):
    """Response for /tenant.json endpoint."""

    slug: str
    name: str
    logo_url: Optional[str] = None
    primary_color: str = "#1a73e8"
    secondary_color: str = "#ea4335"
    features: dict = {}


class TenantDetailResponse(BaseModel):
    """Detailed tenant information."""

    id: UUID
    nome: str
    slug: str
    cnpj: Optional[str] = None
    email: str
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    ativo: bool
    branding: Optional[TenantBrandingResponse] = None

    class Config:
        from_attributes = True



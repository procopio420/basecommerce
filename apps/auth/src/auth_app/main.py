"""
Auth Service - Centralized authentication for BaseCommerce.

This service handles:
- User authentication (login/logout)
- JWT token creation and validation
- Tenant resolution and branding
"""

from datetime import timedelta
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from basecore.logging import setup_logging
from basecore.security import create_access_token, get_password_hash, verify_password
from basecore.settings import get_settings

from auth_app.deps import (
    get_current_user,
    get_db,
    get_tenant_branding,
    get_tenant_by_slug,
    get_tenant_from_header,
    get_tenant_slug_from_header,
    require_admin_user,
    require_current_user,
)
from auth_app.models import Tenant, TenantBranding, User
from auth_app.schemas import (
    LoginRequest,
    TenantResponse,
    TokenResponse,
    UserCreate,
    UserCreatedResponse,
    UserResponse,
)
from auth_app.utils import generate_random_password

setup_logging()
settings = get_settings()

app = FastAPI(
    title="Auth Service",
    description="Centralized authentication service for BaseCommerce platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# =============================================================================
# Health Check
# =============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "auth"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Auth Service", "version": "1.0.0"}


# =============================================================================
# Tenant JSON Endpoint
# =============================================================================


@app.get("/tenant.json", response_model=TenantResponse)
async def tenant_json(
    tenant: Optional[Tenant] = Depends(get_tenant_from_header),
    db: Session = Depends(get_db),
):
    """
    Return tenant branding as JSON.
    
    Uses X-Tenant-Slug header (set by Nginx) to identify tenant.
    Returns default branding if tenant not found.
    """
    if not tenant:
        return TenantResponse(
            slug="",
            name="BaseCommerce",
            logo_url=None,
            primary_color="#1a73e8",
            secondary_color="#ea4335",
            features={},
        )

    branding = get_tenant_branding(db, tenant.id)

    return TenantResponse(
        slug=tenant.slug,
        name=tenant.nome,
        logo_url=branding.logo_url if branding else None,
        primary_color=branding.primary_color if branding else "#1a73e8",
        secondary_color=branding.secondary_color if branding else "#ea4335",
        features=branding.feature_flags if branding else {},
    )


# =============================================================================
# JSON Login Endpoint (API)
# =============================================================================


@app.post("/login", response_model=TokenResponse)
async def login_json(
    login_request: LoginRequest,
    tenant_slug: Optional[str] = Depends(get_tenant_slug_from_header),
    db: Session = Depends(get_db),
):
    """
    Login via JSON body (for API clients).
    
    Returns JWT token on success.
    """
    # Determine tenant slug (from request body or header)
    slug = login_request.tenant_slug or tenant_slug

    if not slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant slug required (via body or X-Tenant-Slug header)",
        )

    # Find tenant
    tenant = get_tenant_by_slug(db, slug)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive",
        )

    # Find user
    user = (
        db.query(User)
        .filter(
            User.email == login_request.email,
            User.tenant_id == tenant.id,
            User.ativo == True,  # noqa: E712
        )
        .first()
    )

    if not user or not verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
            "role": user.role,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(access_token=access_token)


# =============================================================================
# Form Login Endpoint (Web)
# =============================================================================


@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    tenant: Optional[Tenant] = Depends(get_tenant_from_header),
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Render login page."""
    # If already logged in, redirect to dashboard
    if user:
        return RedirectResponse(url="/web/dashboard", status_code=302)

    branding = get_tenant_branding(db, tenant.id) if tenant else None

    context = {
        "request": request,
        "tenant_name": tenant.nome if tenant else "BaseCommerce",
        "branding": branding,
        "error": None,
    }

    return templates.TemplateResponse("login.html", context)


@app.post("/login/form")
async def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    tenant_slug: Optional[str] = Depends(get_tenant_slug_from_header),
    db: Session = Depends(get_db),
):
    """
    Handle login form submission.
    
    Sets httponly cookie and redirects to dashboard.
    """
    # Find tenant
    tenant = get_tenant_by_slug(db, tenant_slug) if tenant_slug else None
    branding = get_tenant_branding(db, tenant.id) if tenant else None

    def render_error(error_msg: str):
        context = {
            "request": request,
            "tenant_name": tenant.nome if tenant else "BaseCommerce",
            "branding": branding,
            "error": error_msg,
        }
        return templates.TemplateResponse("login.html", context, status_code=401)

    if not tenant:
        return render_error("Tenant não especificado")

    # Find user
    user = (
        db.query(User)
        .filter(
            User.email == email,
            User.tenant_id == tenant.id,
            User.ativo == True,  # noqa: E712
        )
        .first()
    )

    if not user or not verify_password(password, user.password_hash):
        return render_error("Email ou senha incorretos")

    # Create token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
            "role": user.role,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Set cookie and redirect
    response = RedirectResponse(url="/web/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return response


# =============================================================================
# Logout Endpoint
# =============================================================================


@app.get("/logout")
async def logout():
    """Clear auth cookie and redirect to login."""
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response


# =============================================================================
# User Info Endpoint
# =============================================================================


@app.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_current_user)):
    """Get current user info."""
    return UserResponse.model_validate(user)


# =============================================================================
# Token Validation Endpoint (for other services)
# =============================================================================


@app.get("/validate")
async def validate_token(user: Optional[User] = Depends(get_current_user)):
    """
    Validate token and return user info.
    
    This endpoint can be used by other services to validate tokens.
    Returns 200 with user info if valid, 401 if invalid.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "valid": True,
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role,
    }


# =============================================================================
# User Management Endpoint
# =============================================================================


@app.post("/users", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
):
    """
    Create a new user for the current tenant.
    
    Requires:
    - Authentication (JWT token)
    - Admin role in the tenant
    
    Validates:
    - Email is unique within the tenant
    - Role is valid (admin or vendedor)
    - Tenant exists and is active
    
    If password is not provided, generates a random password automatically.
    """
    # Validate role
    if user_create.role not in ["admin", "vendedor"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'admin' or 'vendedor'",
        )

    # Verify tenant is active (already verified by require_admin_user)
    tenant_id = current_user.tenant_id

    # Check if email already exists in this tenant
    existing_user = (
        db.query(User)
        .filter(
            User.email == user_create.email,
            User.tenant_id == tenant_id,
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user_create.email}' already exists in this tenant",
        )

    # Generate password if not provided
    password = user_create.password or generate_random_password()
    password_hash = get_password_hash(password)

    # Create user
    new_user = User(
        tenant_id=tenant_id,
        nome=user_create.nome,
        email=user_create.email,
        password_hash=password_hash,
        role=user_create.role,
        ativo=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Prepare response - include password only if it was auto-generated
    response_data = {
        "id": new_user.id,
        "tenant_id": new_user.tenant_id,
        "nome": new_user.nome,
        "email": new_user.email,
        "role": new_user.role,
        "ativo": new_user.ativo,
        "password": None if user_create.password else password,
    }

    return UserCreatedResponse(**response_data)

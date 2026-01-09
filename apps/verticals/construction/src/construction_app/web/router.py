"""Web router for server-rendered HTMX pages."""

from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from construction_app.application.services.cotacao_service import CotacaoService
from construction_app.application.services.pedido_service import PedidoService
from construction_app.core.database import get_db
from construction_app.domain.cotacao.exceptions import (
    CotacaoNaoPodeSerAprovadaException,
    CotacaoNaoPodeSerEditadaException,
    CotacaoNaoPodeSerEnviadaException,
)
from construction_app.domain.pedido.exceptions import (
    CotacaoNaoAprovadaException,
    CotacaoSemItensException,
    PedidoNaoPodeSerCanceladoException,
)
from construction_app.models.cotacao import Cotacao
from construction_app.models.pedido import Pedido
from construction_app.web.deps import UserClaims, get_optional_web_user, require_web_user
from construction_app.web.middleware import DefaultBranding

# Setup templates
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

web_router = APIRouter()


def get_template_context(
    request: Request,
    user: Optional[UserClaims] = None,
    **extra_context,
) -> dict:
    """Build common template context with tenant branding.
    
    Note: Tenant branding is now fetched client-side via /tenant.json
    which is served by the auth service.
    """
    tenant_slug = getattr(request.state, "tenant_slug", None)
    branding = DefaultBranding()
    
    return {
        "request": request,
        "user": user,
        "tenant_name": tenant_slug.capitalize() if tenant_slug else "BaseCommerce",
        "tenant_slug": tenant_slug,
        "branding": branding,
        **extra_context,
    }


# =============================================================================
# Authentication Routes (redirect to auth service)
# =============================================================================

@web_router.get("/login")
async def login_redirect():
    """Redirect to auth service login page."""
    return RedirectResponse(url="/auth/login", status_code=302)


@web_router.get("/logout")
async def logout_redirect():
    """Redirect to auth service logout."""
    return RedirectResponse(url="/auth/logout", status_code=302)


# =============================================================================
# Dashboard
# =============================================================================

@web_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """Render dashboard page with summary stats."""
    tenant_id = user.tenant_id
    
    # Get counts
    cotacoes_count = db.query(Cotacao).filter(Cotacao.tenant_id == tenant_id).count()
    pedidos_count = db.query(Pedido).filter(Pedido.tenant_id == tenant_id).count()
    
    # Recent cotações
    cotacoes_recentes = (
        db.query(Cotacao)
        .filter(Cotacao.tenant_id == tenant_id)
        .order_by(Cotacao.created_at.desc())
        .limit(5)
        .all()
    )
    
    context = get_template_context(
        request,
        user=user,
        cotacoes_count=cotacoes_count,
        pedidos_count=pedidos_count,
        cotacoes_recentes=cotacoes_recentes,
    )
    return templates.TemplateResponse("pages/dashboard.html", context)


# =============================================================================
# Cotações
# =============================================================================

@web_router.get("/cotacoes", response_class=HTMLResponse)
async def cotacoes_list_page(
    request: Request,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """Render cotações list page."""
    tenant_id = user.tenant_id
    
    cotacoes = (
        db.query(Cotacao)
        .filter(Cotacao.tenant_id == tenant_id)
        .order_by(Cotacao.created_at.desc())
        .limit(100)
        .all()
    )
    
    context = get_template_context(request, user=user, cotacoes=cotacoes)
    return templates.TemplateResponse("pages/cotacoes_list.html", context)


@web_router.get("/cotacoes/table", response_class=HTMLResponse)
async def cotacoes_table_partial(
    request: Request,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """HTMX partial: return just the cotações table."""
    tenant_id = user.tenant_id
    
    cotacoes = (
        db.query(Cotacao)
        .filter(Cotacao.tenant_id == tenant_id)
        .order_by(Cotacao.created_at.desc())
        .limit(100)
        .all()
    )
    
    context = get_template_context(request, user=user, cotacoes=cotacoes)
    return templates.TemplateResponse("partials/table_cotacoes.html", context)


@web_router.post("/cotacoes/{cotacao_id}/enviar", response_class=HTMLResponse)
async def enviar_cotacao(
    request: Request,
    cotacao_id: UUID,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """Send cotação (change status to 'enviada')."""
    service = CotacaoService(db)
    
    try:
        cotacao = service.enviar_cotacao(cotacao_id=cotacao_id, tenant_id=user.tenant_id)
        
        context = get_template_context(
            request,
            user=user,
            cotacoes=[cotacao],
            flash_message="Cotação enviada com sucesso!",
            flash_type="success",
        )
        response = templates.TemplateResponse("partials/table_cotacoes.html", context)
        response.headers["HX-Trigger"] = "cotacaoUpdated"
        return response
        
    except CotacaoNaoPodeSerEnviadaException as e:
        return _flash_error(request, user, str(e))
    except ValueError as e:
        return _flash_error(request, user, str(e))


@web_router.post("/cotacoes/{cotacao_id}/aprovar", response_class=HTMLResponse)
async def aprovar_cotacao(
    request: Request,
    cotacao_id: UUID,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """Approve cotação (change status to 'aprovada')."""
    service = CotacaoService(db)
    
    try:
        cotacao = service.aprovar_cotacao(cotacao_id=cotacao_id, tenant_id=user.tenant_id)
        
        context = get_template_context(
            request,
            user=user,
            cotacoes=[cotacao],
            flash_message="Cotação aprovada com sucesso!",
            flash_type="success",
        )
        response = templates.TemplateResponse("partials/table_cotacoes.html", context)
        response.headers["HX-Trigger"] = "cotacaoUpdated"
        return response
        
    except CotacaoNaoPodeSerAprovadaException as e:
        return _flash_error(request, user, str(e))
    except ValueError as e:
        return _flash_error(request, user, str(e))


@web_router.post("/cotacoes/{cotacao_id}/cancelar", response_class=HTMLResponse)
async def cancelar_cotacao(
    request: Request,
    cotacao_id: UUID,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """Cancel cotação."""
    service = CotacaoService(db)
    
    try:
        cotacao = service.cancelar_cotacao(cotacao_id=cotacao_id, tenant_id=user.tenant_id)
        
        context = get_template_context(
            request,
            user=user,
            cotacoes=[cotacao],
            flash_message="Cotação cancelada.",
            flash_type="warning",
        )
        response = templates.TemplateResponse("partials/table_cotacoes.html", context)
        response.headers["HX-Trigger"] = "cotacaoUpdated"
        return response
        
    except CotacaoNaoPodeSerEditadaException as e:
        return _flash_error(request, user, str(e))
    except ValueError as e:
        return _flash_error(request, user, str(e))


# =============================================================================
# Pedidos
# =============================================================================

@web_router.get("/pedidos", response_class=HTMLResponse)
async def pedidos_list_page(
    request: Request,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """Render pedidos list page."""
    tenant_id = user.tenant_id
    
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.tenant_id == tenant_id)
        .order_by(Pedido.created_at.desc())
        .limit(100)
        .all()
    )
    
    context = get_template_context(request, user=user, pedidos=pedidos)
    return templates.TemplateResponse("pages/pedidos_list.html", context)


@web_router.get("/pedidos/table", response_class=HTMLResponse)
async def pedidos_table_partial(
    request: Request,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """HTMX partial: return just the pedidos table."""
    tenant_id = user.tenant_id
    
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.tenant_id == tenant_id)
        .order_by(Pedido.created_at.desc())
        .limit(100)
        .all()
    )
    
    context = get_template_context(request, user=user, pedidos=pedidos)
    return templates.TemplateResponse("partials/table_pedidos.html", context)


@web_router.post("/pedidos/from-cotacao/{cotacao_id}", response_class=HTMLResponse)
async def criar_pedido_from_cotacao(
    request: Request,
    cotacao_id: UUID,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """Convert approved cotação to pedido."""
    service = PedidoService(db)
    
    try:
        pedido = service.converter_cotacao_em_pedido(
            cotacao_id=cotacao_id,
            tenant_id=user.tenant_id,
            usuario_id=user.id,
        )
        
        # Redirect to pedidos page with success message
        response = Response(status_code=200)
        response.headers["HX-Redirect"] = "/web/pedidos"
        return response
        
    except (CotacaoNaoAprovadaException, CotacaoSemItensException) as e:
        return _flash_error(request, user, str(e))
    except ValueError as e:
        return _flash_error(request, user, str(e))


@web_router.post("/pedidos/{pedido_id}/cancelar", response_class=HTMLResponse)
async def cancelar_pedido(
    request: Request,
    pedido_id: UUID,
    user: UserClaims = Depends(require_web_user),
    db: Session = Depends(get_db),
):
    """Cancel pedido."""
    service = PedidoService(db)
    
    try:
        pedido = service.cancelar_pedido(pedido_id=pedido_id, tenant_id=user.tenant_id)
        
        context = get_template_context(
            request,
            user=user,
            pedidos=[pedido],
            flash_message="Pedido cancelado.",
            flash_type="warning",
        )
        response = templates.TemplateResponse("partials/table_pedidos.html", context)
        response.headers["HX-Trigger"] = "pedidoUpdated"
        return response
        
    except PedidoNaoPodeSerCanceladoException as e:
        return _flash_error(request, user, str(e))
    except ValueError as e:
        return _flash_error(request, user, str(e))


# =============================================================================
# Helpers
# =============================================================================

def _flash_error(request: Request, user: UserClaims, message: str) -> HTMLResponse:
    """Return a flash error partial."""
    context = get_template_context(
        request,
        user=user,
        flash_message=message,
        flash_type="error",
    )
    return templates.TemplateResponse("partials/flash.html", context)

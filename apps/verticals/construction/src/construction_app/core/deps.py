"""API dependencies for Bearer token authentication."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from construction_app.core.security import decode_access_token

security = HTTPBearer()


@dataclass
class UserClaims:
    """User information extracted from JWT token.
    
    This replaces the User model for authentication purposes.
    User data is stored in auth service, vertical only needs claims.
    """
    id: UUID
    tenant_id: UUID
    email: str
    role: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserClaims:
    """
    Dependency para obter o usuário atual através do token JWT.
    Extrai claims do token sem query ao banco.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[str] = payload.get("sub")
    tenant_id: Optional[str] = payload.get("tenant_id")
    email: Optional[str] = payload.get("email")
    role: Optional[str] = payload.get("role", "vendedor")

    if not user_id or not tenant_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserClaims(
        id=UUID(user_id),
        tenant_id=UUID(tenant_id),
        email=email,
        role=role,
    )


async def get_tenant_id(current_user: UserClaims = Depends(get_current_user)) -> UUID:
    """Dependency para garantir que todas as queries tenham tenant_id."""
    return current_user.tenant_id


async def require_admin_role(current_user: UserClaims = Depends(get_current_user)) -> UserClaims:
    """
    Dependency para garantir que apenas admins podem acessar endpoints.
    Levanta HTTPException 403 se usuário não for admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar este recurso.",
        )
    return current_user

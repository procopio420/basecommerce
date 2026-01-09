"""
Shared dependencies for FastAPI applications.

NOTE: This module provides BASE dependencies that can be used by any vertical.
For dependencies that require vertical-specific models (like User), 
each vertical should define its own deps module that imports and extends these.

Example usage in a vertical:
    from basecore.deps import decode_token_payload
    
    # Then define vertical-specific user loading
    async def get_current_user(...):
        payload = decode_token_payload(token)
        # Load user from vertical's own User model
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from basecore.security import decode_access_token

security = HTTPBearer()


def decode_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Decode JWT token and return payload.
    
    This is a base dependency that can be used by verticals.
    Each vertical should implement its own get_current_user that
    loads the user from the vertical's User model.
    
    Returns:
        dict with at least 'sub' (user_id) and 'tenant_id'
    
    Raises:
        HTTPException 401 if token is invalid
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    tenant_id: str | None = payload.get("tenant_id")

    if user_id is None or tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

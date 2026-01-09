"""
Auth API endpoints.

Note: Login is now handled by the auth service at /auth/login.
This module only provides a redirect endpoint for backwards compatibility.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/login")
async def login_redirect():
    """
    Login is now handled by auth service.
    
    Use POST /auth/login for JSON login.
    Use GET /auth/login for web login.
    """
    return JSONResponse(
        status_code=308,
        content={
            "message": "Login moved to auth service",
            "redirect": "/auth/login",
        },
        headers={"Location": "/auth/login"},
    )

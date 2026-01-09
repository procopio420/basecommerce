from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    tenant_id: str | None = None  # Opcional para login inicial


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str | None = None
    tenant_id: str | None = None

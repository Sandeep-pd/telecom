"""Authentication routes for demo and secure access."""

import hmac

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.core.security import create_access_token, require_access_token
from app.schemas.auth import AuthRequest, AuthToken

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/token", response_model=AuthToken)
async def create_token(payload: AuthRequest) -> AuthToken:
    if not (
        hmac.compare_digest(
            payload.username.encode("utf-8"),
            settings.admin_username.encode("utf-8"),
        )
        and hmac.compare_digest(
            payload.password.encode("utf-8"),
            settings.admin_password.encode("utf-8"),
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthToken(
        access_token=create_access_token(payload.username),
        username=payload.username,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/validate")
async def validate_token(username: str = Depends(require_access_token)) -> dict[str, str]:
    return {"status": "valid", "username": username}

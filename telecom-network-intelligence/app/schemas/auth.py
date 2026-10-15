"""Authentication request and response schemas."""

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    expires_in: int

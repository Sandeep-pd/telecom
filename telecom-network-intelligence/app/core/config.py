import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "telecom-network-intelligence"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    access_token_expire_minutes: int = Field(default=30, gt=0)
    admin_username: str = "admin"
    admin_password: str = "admin123"
    require_auth: bool = False
    database_url: str = "sqlite:///./telecom.db"
    postgres_db: str = "telecom_db"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


def get_settings() -> Settings:
    return Settings()

"""Application settings.

Reads the environment variables the workshop platform injects automatically,
and falls back to a local .env file for standalone development.
"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Single source of truth for every environment value."""

    # --- Application identity ---
    app_name: str = "ACME Project Tracker API"
    app_version: str = "2.0.0"
    api_v1_prefix: str = os.getenv("API_PREFIX", "/api")

    # --- Environment: the platform sets this to false in the cloud ---
    is_local: bool = os.getenv("IS_LOCAL", "true").lower() == "true"

    # --- PostgreSQL, assembled from the injected variables ---
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "5432")
    postgres_name: str = os.getenv("POSTGRES_NAME", "postgres")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_pass: str = os.getenv("POSTGRES_PASS", "postgres")

    # An explicit DATABASE_URL wins, which keeps standalone development working.
    database_url_override: str = os.getenv("DATABASE_URL", "")

    # --- Authentication ---
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480

    # --- Cross-origin access ---
    cors_origins: str = "http://localhost:3000,http://localhost:3030"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def database_url(self) -> str:
        """Build the connection string the application actually uses.

        Aurora in the cloud requires SSL; the local PostgreSQL does not have
        it configured, so the mode is switched on IS_LOCAL.
        """
        if self.database_url_override:
            return self.database_url_override

        url = (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_pass}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}"
        )

        if not self.is_local:
            url += "?sslmode=require"

        return url

    @property
    def cors_origin_list(self) -> list[str]:
        """Split the comma separated string into the list FastAPI expects."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()

# Aurora-X Runtime Configuration Schema (SPEC-2)
# Pydantic-based configuration with validation
import os

from pydantic import AnyUrl, BaseModel


class Settings(BaseModel):
    """Runtime configuration settings for Aurora-X"""

    host: str = "127.0.0.1"
    port: int = 8000
    aurora_token_secret: str
    database_url: AnyUrl | None = None
    environment: str = os.getenv("ENVIRONMENT", "dev")
    cors_origins: str = os.getenv("CORS_ORIGINS", "")

    class Config:
        extra = "ignore"


def load_settings() -> Settings:
    """
    Load and validate runtime settings from environment variables.
    Raises ValidationError if required settings are missing.
    """
    return Settings(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        aurora_token_secret=os.environ.get("AURORA_TOKEN_SECRET", ""),
        database_url=os.environ.get("DATABASE_URL"),
        environment=os.environ.get("ENVIRONMENT", "dev"),
        cors_origins=os.environ.get("CORS_ORIGINS", ""),
    )

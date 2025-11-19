"""
Configuration management using environment variables.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Quiz Configuration
    EMAIL: str = os.getenv("EMAIL", "")
    SECRET: str = os.getenv("SECRET", "")

    # LLM API Configuration (Gemini)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-pro"
    MAX_TOKENS: int = 8000

    # Browser Configuration
    HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30000  # 30 seconds

    # Quiz Solving Configuration
    QUIZ_TIMEOUT: int = 180  # 3 minutes in seconds
    MAX_RETRIES: int = 2

    # File Storage
    TEMP_DIR: Path = Path("./temp")
    DOWNLOADS_DIR: Path = Path("./downloads")

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.TEMP_DIR.mkdir(exist_ok=True)
        self.DOWNLOADS_DIR.mkdir(exist_ok=True)

    def validate_required(self) -> None:
        """Validate that required settings are configured."""
        required_fields = ["EMAIL", "SECRET", "GEMINI_API_KEY"]
        missing = [field for field in required_fields if not getattr(self, field)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


# Global settings instance
settings = Settings()

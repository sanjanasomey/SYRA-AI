"""
SYRA AI - Application Configuration
Module: backend/core/config.py

Centralised settings loaded from environment variables using
pydantic-settings. Never exposes raw API keys in responses.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Walk up from backend/core/ to project root to find .env if it exists
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_env_path = os.path.join(_project_root, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)


class Settings(BaseSettings):
    """Application-wide settings sourced from environment variables."""

    # --- API Keys (read from .env, never returned in responses) ---
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # --- Model defaults ---
    default_provider: str = "gemini"
    default_model: str = "gemini-flash-lite-latest"
    default_temperature: float = 0.7
    default_max_tokens: int = 1024

    # --- Server ---
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    app_title: str = "SYRA AI"
    app_version: str = "2.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# Singleton instance
settings = Settings()

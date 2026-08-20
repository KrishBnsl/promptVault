"""Settings management for PromptVault."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

DEFAULT_MODEL_CONFIG = {
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "temperature": 0.0,
    "max_tokens": 512,
}


class Settings(BaseSettings):
    """PromptVault settings loaded from environment variables."""

    db_path: str = os.getenv("PROMPTVAULT_DB_PATH", "./promptvault.db")
    default_provider: str = os.getenv("PROMPTVAULT_DEFAULT_PROVIDER", "openai")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "openai")

    @property
    def database_url(self) -> str:
        """Get the SQLite database URL."""
        db_path = Path(self.db_path).resolve()
        return f"sqlite:///{db_path}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

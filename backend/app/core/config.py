"""Application configuration using pydantic-settings."""

import json
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    app_name: str = "Kumon Marker"
    app_version: str = "0.5.3"  # Can be overridden by APP_VERSION env var
    image_tag: str = "local"  # Container image tag, set by IMAGE_TAG env var
    debug: bool = False

    # Analysis mode: "ollama" (recommended), "gemini", "api" (Anthropic), or "cli" (Claude Code CLI)
    claude_mode: str = "ollama"
    claude_model: str = "claude-sonnet-4-20250514"  # Model for Claude Code CLI

    # Ollama (only used when claude_mode="ollama") - local LLM, no rate limits
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "moondream"

    # Anthropic (only used when claude_mode="api")
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Google Gemini (only used when claude_mode="gemini")
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Google OAuth (from Helm/env vars)
    google_client_id: str = ""
    google_client_secret: str = ""

    # Google Drive
    gdrive_folder: str = "From_BrotherDevice"

    # Worksheet analysis
    questions_per_page: int = 10
    custom_prompt: str = ""

    # Paths
    data_dir: str = "/app/data"

    # Multi-user auth
    allowed_users: str = ""  # Comma-separated list of allowed email addresses
    session_secret: str = "change-me-in-production"  # Secret for signing session cookies

    # Timezone for date display (IANA timezone name, e.g. "Australia/Sydney")
    timezone: str = "Australia/Sydney"

    # Job queue - limit concurrent processing jobs
    max_concurrent_jobs: int = 1

    # RabbitMQ configuration
    rabbitmq_url: str = ""  # e.g., amqp://user:pass@host:5672/

    # PostgreSQL configuration
    database_url: str = ""  # e.g., postgresql://user:pass@host:5432/db

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_allowed_users_list(self) -> list[str]:
        """Get list of allowed user emails."""
        if not self.allowed_users:
            return []
        return [email.strip().lower() for email in self.allowed_users.split(",") if email.strip()]


settings = Settings()


def get_runtime_settings_path() -> Path:
    """Get path to runtime settings file."""
    return Path(settings.data_dir) / "settings.json"


def get_runtime_settings() -> dict:
    """Load runtime settings (user overrides)."""
    path = get_runtime_settings_path()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_runtime_settings(data: dict) -> None:
    """Save runtime settings."""
    path = get_runtime_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def get_effective_setting(key: str, default=None):
    """Get effective setting value (runtime override > env > default)."""
    runtime = get_runtime_settings()
    if key in runtime:
        return runtime[key]
    return getattr(settings, key, default)

"""Application configuration via pydantic-settings.

All settings are loaded from environment variables with sensible defaults.
For local development, copy `.env.example` to `.env`.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings.

    Values are resolved in this order:
    1. Environment variables
    2. `.env` file (if present)
    3. Defaults defined here
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── API ─────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # ── Security ────────────────────────────────────────────────
    webhook_secret: str = "change-me-in-production"

    # ── GitHub ──────────────────────────────────────────────────
    github_token: str = ""
    github_org: str = ""
    github_repo: str = ""

    # ── Sentinel ────────────────────────────────────────────────
    sentinel_id: str = ""
    sentinel_poll_interval: int = 60
    sentinel_task_timeout_minutes: int = 120

    # ── Redis ───────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── PostgreSQL ──────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://osapow:osapow@localhost:5432/osapow"

    # ── Shell Bridge ────────────────────────────────────────────
    shell_bridge_path: str = "./scripts/devcontainer-opencode.sh"


settings = Settings()

"""Central application settings loaded from environment variables (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BACKEND_DIR / ".env")
load_dotenv()


def _get(key: str, default: str = "") -> str:
    value = os.getenv(key)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


@dataclass(frozen=True)
class ProviderSettings:
    """Connection settings for one OpenAI-compatible remote provider."""

    name: str
    api_key: str
    base_url: str
    model: str


@dataclass
class Settings:
    # --- App ---
    app_name: str = "Autonomous Research Platform"
    version: str = "4.0"
    host: str = _get("HOST", "0.0.0.0")
    port: int = int(_get("PORT", "8679"))
    cors_origins: list[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in _get("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
            if o.strip()
        ]
    )

    # --- Storage ---
    data_dir: Path = Path(_get("RESEARCH_DATA_DIR", str(BACKEND_DIR / "data")))
    reports_dir: Path = Path(_get("RESEARCH_REPORTS_DIR", str(BACKEND_DIR / "reports")))

    # --- LLM selection ---
    # One of: auto | openrouter | groq | openai | gemini | ollama
    llm_provider: str = _get("LLM_PROVIDER", "auto").lower()

    # Optional per-stage routing: route each agent to a different provider.
    # Empty means "use the global LLM_PROVIDER". Example: run the critic on
    # free local Ollama while drafting with a hosted frontier model.
    planner_provider: str = _get("PLANNER_PROVIDER").lower()
    writer_provider: str = _get("WRITER_PROVIDER").lower()
    critic_provider: str = _get("CRITIC_PROVIDER").lower()

    # --- Ollama (local models) ---
    ollama_base_url: str = _get("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_chat_model: str = _get("OLLAMA_CHAT_MODEL", "llama3.1:8b-instruct-q4_K_M")
    ollama_embed_model: str = _get("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    # --- Remote providers (any provider with an API key becomes usable) ---
    openrouter_api_key: str = _get("OPENROUTER_API_KEY")
    openrouter_base_url: str = _get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_model: str = _get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

    groq_api_key: str = _get("GROQ_API_KEY")
    groq_base_url: str = _get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    groq_model: str = _get("GROQ_MODEL", "llama-3.3-70b-versatile")

    openai_api_key: str = _get("OPENAI_API_KEY")
    openai_base_url: str = _get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = _get("OPENAI_MODEL", "gpt-4o-mini")

    gemini_api_key: str = _get("GEMINI_API_KEY") or _get("GOOGLE_API_KEY")
    gemini_model: str = _get("GEMINI_MODEL", "gemini-2.0-flash")

    # --- Request behaviour ---
    llm_timeout_seconds: float = float(_get("LLM_TIMEOUT_SECONDS", "180"))
    llm_max_retries: int = int(_get("LLM_MAX_RETRIES", "2"))
    max_revision_loops: int = int(_get("MAX_REVISION_LOOPS", "3"))
    critic_pass_score: float = float(_get("CRITIC_PASS_SCORE", "7.0"))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "research.db"

    @property
    def db_path_str(self) -> str:
        self.ensure_dirs()
        return str(self.db_path)

    # ------------------------------------------------------------------
    # Providers
    # ------------------------------------------------------------------
    def provider_settings(self) -> dict[str, ProviderSettings]:
        return {
            "openrouter": ProviderSettings(
                "openrouter", self.openrouter_api_key, self.openrouter_base_url, self.openrouter_model
            ),
            "groq": ProviderSettings("groq", self.groq_api_key, self.groq_base_url, self.groq_model),
            "openai": ProviderSettings("openai", self.openai_api_key, self.openai_base_url, self.openai_model),
            "ollama": ProviderSettings("ollama", "", self.ollama_base_url, self.ollama_chat_model),
        }

    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    def fallback_order(self) -> list[str]:
        """Priority order used when LLM_PROVIDER=auto."""
        order = []
        for name, provider in self.provider_settings().items():
            if name == "ollama":
                continue
            if provider.api_key:
                order.append(name)
        if self.gemini_configured():
            order.append("gemini")
        order.append("ollama")
        return order


settings = Settings()

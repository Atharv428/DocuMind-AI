from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass
class Settings:
    project_root: Path = BASE_DIR
    uploads_path: Path = Path(os.getenv("UPLOADS_PATH", str(BASE_DIR / "data" / "uploads")))
    chroma_path: Path = Path(os.getenv("CHROMA_PATH", str(BASE_DIR / "data" / "chroma")))
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "600"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    top_k: int = int(os.getenv("TOP_K", "4"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
    allowed_extensions: set[str] = None

    def __post_init__(self):
        self.uploads_path = Path(self.uploads_path)
        self.chroma_path = Path(self.chroma_path)
        self.uploads_path.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        if self.allowed_extensions is None:
            self.allowed_extensions = {".pdf"}

    @property
    def document_index_path(self) -> Path:
        return self.project_root / "data" / "documents.json"

    @property
    def chat_index_path(self) -> Path:
        return self.project_root / "data" / "chat_history.json"


settings = Settings()


def reload_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env", override=True)
    settings.llm_provider = os.getenv("LLM_PROVIDER", "ollama")
    settings.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    settings.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    settings.ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    settings.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    settings.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    settings.embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    settings.chunk_size = int(os.getenv("CHUNK_SIZE", str(settings.chunk_size)))
    settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", str(settings.chunk_overlap)))
    settings.top_k = int(os.getenv("TOP_K", str(settings.top_k)))
    settings.temperature = float(os.getenv("TEMPERATURE", str(settings.temperature)))
    return settings


def save_setting_to_env(key: str, value: str) -> bool:
    env_path = BASE_DIR / ".env"
    try:
        content = ""
        if env_path.exists():
            content = env_path.read_text(encoding="utf-8")

        lines = content.splitlines()
        found = False
        new_lines = []
        prefix = f"{key.strip()}="
        for line in lines:
            if line.strip().startswith(prefix):
                new_lines.append(f"{key.strip()}={value.strip()}")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"{key.strip()}={value.strip()}")

        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        reload_settings()
        return True
    except Exception:
        return False


def save_api_key_to_env(api_key: str) -> bool:
    return save_setting_to_env("GEMINI_API_KEY", api_key)

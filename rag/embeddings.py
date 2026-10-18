from __future__ import annotations

from typing import Sequence

from sentence_transformers import SentenceTransformer

from .config import settings


class EmbeddingService:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self.model = self._load_model()

    def _load_model(self) -> SentenceTransformer:
        try:
            return SentenceTransformer(self.model_name)
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                f"Unable to load the embedding model '{self.model_name}'. Please install or configure it correctly."
            ) from exc

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(list(texts), convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, question: str) -> list[float]:
        result = self.embed_texts([question])
        return result[0] if result else []

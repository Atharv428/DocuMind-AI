from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rag.config import settings


class DocumentService:
    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = Path(storage_path) if storage_path is not None else settings.document_index_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return {"documents": []}
        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {"documents": []}

    def _save(self, data: dict[str, Any]) -> None:
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def add_document(self, document: dict[str, Any]) -> None:
        payload = self._load()
        docs = payload.setdefault("documents", [])
        if not any(item.get("document_id") == document.get("document_id") for item in docs):
            docs.append(document)
        self._save(payload)

    def list_documents(self) -> list[dict[str, Any]]:
        return self._load().get("documents", [])

    def delete_document(self, document_id: str) -> None:
        payload = self._load()
        updated = [item for item in payload.get("documents", []) if item.get("document_id") != document_id]
        payload["documents"] = updated
        self._save(payload)

    def find_by_hash(self, file_hash: str) -> dict[str, Any] | None:
        for item in self.list_documents():
            if item.get("hash") == file_hash:
                return item
        return None

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        for item in self.list_documents():
            if item.get("document_id") == document_id:
                return item
        return None


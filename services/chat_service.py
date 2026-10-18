from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from rag.config import settings


class ChatService:
    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = Path(storage_path) if storage_path is not None else settings.chat_index_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return {"sessions": []}
        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {"sessions": []}

    def _save(self, data: dict[str, Any]) -> None:
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def create_session(self, title: str = "New chat") -> dict[str, Any]:
        payload = self._load()
        unique_id = f"chat-{uuid.uuid4().hex[:8]}"
        session = {"session_id": unique_id, "title": title, "messages": []}
        payload.setdefault("sessions", []).append(session)
        self._save(payload)
        return session

    def list_sessions(self) -> list[dict[str, Any]]:
        return self._load().get("sessions", [])

    def add_message(self, session_id: str, role: str, content: str, citations: list[dict[str, Any]] | None = None) -> None:
        payload = self._load()
        for session in payload.get("sessions", []):
            if session.get("session_id") == session_id:
                session.setdefault("messages", []).append(
                    {
                        "role": role,
                        "content": content,
                        "citations": citations or [],
                    }
                )
                # Auto-generate meaningful session title from first user message
                current_title = str(session.get("title", "")).strip().lower()
                if role == "user" and (not current_title or current_title == "new chat"):
                    clean = content.strip().replace("\n", " ")
                    session["title"] = (clean[:30] + "...") if len(clean) > 30 else clean
                self._save(payload)
                break

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        for session in self.list_sessions():
            if session.get("session_id") == session_id:
                return session
        return None

    def delete_session(self, session_id: str) -> None:
        payload = self._load()
        payload["sessions"] = [session for session in payload.get("sessions", []) if session.get("session_id") != session_id]
        self._save(payload)

    def clear_empty_sessions(self, keep_session_id: str | None = None) -> None:
        payload = self._load()
        cleaned = []
        for s in payload.get("sessions", []):
            if s.get("session_id") == keep_session_id or (s.get("messages") and len(s["messages"]) > 0):
                cleaned.append(s)
        payload["sessions"] = cleaned
        self._save(payload)


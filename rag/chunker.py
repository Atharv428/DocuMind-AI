from __future__ import annotations

import re


def estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r"\S+", text)))


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    if not text or not text.strip():
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [text.strip()] if text.strip() else []

    step = max(1, chunk_size - overlap)
    chunks: list[str] = []
    seen = set()
    for start_index in range(0, len(words), step):
        end_index = min(start_index + chunk_size, len(words))
        fragment = " ".join(words[start_index:end_index]).strip()
        if not fragment:
            continue
        if fragment not in seen:
            chunks.append(fragment)
            seen.add(fragment)
        if end_index >= len(words):
            break
    return chunks


def build_chunks_from_pages(pages: list[dict], chunk_size: int = 600, overlap: int = 100) -> list[dict]:
    chunk_records: list[dict] = []
    for page in pages:
        page_text = page.get("text", "").strip()
        for chunk_index, chunk in enumerate(chunk_text(page_text, chunk_size, overlap), start=1):
            chunk_records.append(
                {
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "token_count": estimate_tokens(chunk),
                }
            )
    return chunk_records

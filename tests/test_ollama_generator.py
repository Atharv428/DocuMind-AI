from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from rag.generator import GeminiGenerator, OllamaGenerator, UnifiedGenerator
from rag.pipeline import RAGPipeline


def test_ollama_generator_build_prompt():
    gen = OllamaGenerator(base_url="http://localhost:11434", model_name="llama3.2:1b")
    prompt = gen._build_prompt("What is DocuMind AI?", ["DocuMind is an intelligent document workspace."])
    assert "DOCUMENT CONTEXT:" in prompt
    assert "DocuMind is an intelligent document workspace." in prompt
    assert "What is DocuMind AI?" in prompt


def test_ollama_check_access_offline():
    gen = OllamaGenerator(base_url="http://127.0.0.1:9999", model_name="llama3.2:1b")
    success, msg = gen.check_access(test_call=False)
    assert success is False
    assert "Cannot connect to Ollama" in msg or "Ollama connection check failed" in msg


def test_ollama_check_access_mock_installed():
    gen = OllamaGenerator(base_url="http://localhost:11434", model_name="llama3.2:1b")
    with patch("urllib.request.urlopen") as mock_url:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {"models": [{"name": "llama3.2:1b"}]}
        ).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_url.return_value = mock_response

        success, msg = gen.check_access(test_call=False)
        assert success is True
        assert "llama3.2:1b" in msg


def test_ollama_generate_chat_format_mock():
    gen = OllamaGenerator(base_url="http://localhost:11434", model_name="llama3.2:1b")
    with patch("urllib.request.urlopen") as mock_url:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {"message": {"role": "assistant", "content": "DocuMind AI leverages local embeddings and Ollama generation."}}
        ).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_url.return_value = mock_response

        answer = gen.generate("Explain DocuMind", ["Passage content"])
        assert "DocuMind AI leverages" in answer


def test_ollama_generate_response_format_mock():
    gen = OllamaGenerator(base_url="http://localhost:11434", model_name="llama3.2:1b")
    with patch("urllib.request.urlopen") as mock_url:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {"response": "DocuMind AI operates in local mode."}
        ).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_url.return_value = mock_response

        answer = gen.generate("Explain DocuMind", ["Passage content"])
        assert "DocuMind AI operates" in answer


def test_unified_generator_selection():
    unified = UnifiedGenerator(provider="retrieval_only")
    assert unified.is_available() is False

    unified.set_provider("ollama")
    assert unified.active_generator is unified.ollama

    unified.set_provider("gemini")
    assert unified.active_generator is unified.gemini

# 🚀 DocuMind AI — Starter Issues & Contribution Backlog

Welcome to the **DocuMind AI** starter issues backlog! These tasks are curated for new contributors, students, and open-source developers looking to make immediate, high-impact contributions to a local-first RAG project.

If you would like to work on one of these issues:
1. Check the [Open Issues](https://github.com/Atharv428/DocuMind-AI/issues) on GitHub.
2. If the issue has not been created yet or is unassigned, open an issue using the templates below or comment on an existing thread expressing interest.
3. Review our [CONTRIBUTING.md](https://github.com/Atharv428/DocuMind-AI/blob/main/CONTRIBUTING.md) guide before submitting your Pull Request!

---

## 📌 Issue #1: Add Actionable Diagnostic Card when Ollama is Offline

- **Title**: `[FEAT] Add actionable troubleshooting alert when Ollama service is unreachable`
- **Labels**: `good first issue`, `enhancement`, `ui`
- **Component**: `app.py` / `ui/components.py`

### 🔍 Problem Statement
When a user launches DocuMind AI without starting the Ollama desktop service or before pulling the required model (`llama3.2:1b`), the application falls back to Local Passage Retrieval mode or displays a status pill. However, first-time users may not know why generation is inactive or what command to run.

### 🎯 Expected Outcome
In `app.py` (specifically in the `Overview` and `Chat with Documents` views), if `current_provider == "ollama"` and `is_engine_ready == False`, render an informative, non-intrusive warning card with:
1. Clear explanation: *"Ollama service is currently unreachable or model is missing."*
2. Copyable terminal snippets:
   - `ollama serve` (to start the daemon)
   - `ollama pull llama3.2:1b` (to pull the recommended model)
3. A *"Retry Connection"* button that re-runs `pipeline.generator.ollama.check_access(test_call=True)` and calls `st.rerun()`.

### ✅ Acceptance Criteria
- [ ] Card only displays when Ollama is selected as the active provider and connection check fails.
- [ ] Does not crash the Streamlit interface if Ollama remains offline.
- [ ] Disappears automatically once the Ollama service becomes reachable.
- [ ] Styled using existing CSS design tokens from `ui/styles.py` (`surface-card`, `status-pill-warning`).

---

## 📌 Issue #2: Support Plain Text (`.txt`) and Markdown (`.md`) Ingestion

- **Title**: `[FEAT] Support plain text (.txt) and Markdown (.md) document ingestion`
- **Labels**: `good first issue`, `enhancement`, `help wanted`
- **Component**: `rag/document_loader.py` / `app.py`

### 🔍 Problem Statement
Currently, `rag/document_loader.py` only extracts and validates PDF documents (`.pdf`). Many developers and researchers have notes, documentation files, and transcripts in `.txt` or `.md` formats that they wish to query using local RAG.

### 🎯 Expected Outcome
Extend `document_loader.py` to support `.txt` and `.md` files alongside `.pdf`:
1. Update `validate_document(file_path)` to accept `.pdf`, `.txt`, and `.md`.
2. Implement `extract_text_file(file_path)`:
   - Reads UTF-8 encoded text with graceful fallback for ISO-8859-1.
   - Normalizes text using existing `normalize_text()`.
   - Simulates page breaks based on word count (e.g., ~500 words per simulated page) or heading sections (`#`) so metadata remains consistent.
3. Update `app.py` file uploader to accept `type=["pdf", "txt", "md"]`.

### ✅ Acceptance Criteria
- [ ] Uploading a valid `.txt` or `.md` file extracts text and preserves document metadata.
- [ ] Word chunking and ChromaDB vector embeddings work identically to PDFs.
- [ ] Existing PDF parsing functionality is completely unaffected.
- [ ] Unit tests added in `tests/test_document_loader.py` covering `.txt` and `.md` extraction.

---

## 📌 Issue #3: Add Comprehensive Unit Tests for NFC Normalization and Corrupted Files

- **Title**: `[TEST] Add unit tests for text normalization, corrupted headers, and password-protected PDFs`
- **Labels**: `good first issue`, `testing`
- **Component**: `tests/test_document_loader.py`

### 🔍 Problem Statement
While `rag/document_loader.py` has validation logic for empty files, magic byte verification, and NFC Unicode normalization, test coverage can be expanded to systematically test malicious or malformed inputs.

### 🎯 Expected Outcome
Add focused pytest test cases in `tests/test_document_loader.py`:
1. `test_normalize_text_strips_control_characters`: Verifies that null bytes (`\x00`), escape characters, and non-printable bytes are stripped while preserving tabs and newlines.
2. `test_normalize_text_collapses_whitespace`: Verifies that 4+ consecutive newlines are collapsed into 2.
3. `test_validate_pdf_rejects_missing_file`: Verifies `ValueError` when a non-existent path is passed.
4. `test_validate_pdf_rejects_oversized_file`: Verifies file size limit handling.

### ✅ Acceptance Criteria
- [ ] All new tests pass with `python -m pytest tests/test_document_loader.py`.
- [ ] No external dependencies or real user files are used (use `tmp_path` fixtures).
- [ ] Test execution takes under 1 second.

---

## 📌 Issue #4: Implement Response Streaming in Chat View

- **Title**: `[FEAT] Implement token streaming for Ollama generation using st.write_stream`
- **Labels**: `enhancement`, `help wanted`
- **Component**: `rag/generator.py` / `app.py`

### 🔍 Problem Statement
Currently, the application waits for the entire LLM generation to complete before displaying the response in the chat panel. For longer answers, this can create a noticeable delay. Ollama natively supports token streaming via `/api/chat` with `stream: true`.

### 🎯 Expected Outcome
1. Add `generate_stream(question: str, context_chunks: list[str]) -> Generator[str, None, None]` to `OllamaGenerator`.
2. Update `app.py` chat message renderer to use Streamlit's `st.write_stream(response_stream)` when streaming is supported.
3. Retain complete answer persistence in `ChatService` after the stream concludes.

### ✅ Acceptance Criteria
- [ ] Tokens appear progressively in the chat UI with smooth rendering.
- [ ] Citations are rendered immediately below the streamed message after generation completes.
- [ ] Fallback to non-streamed `generate()` if the client does not support generator streaming.
- [ ] Persisted chat history accurately records the complete streamed message.

---

## 📌 Issue #5: Add Interactive Welcome Prompts & Demo Document Guidance

- **Title**: `[FEAT] Add interactive quick-start guide and sample query cards for new users`
- **Labels**: `good first issue`, `ui`, `documentation`
- **Component**: `app.py` / `ui/components.py`

### 🔍 Problem Statement
When a user launches DocuMind AI for the first time, the document library and chat history are empty. While empty state containers exist, new contributors and users would benefit from guidance on the types of questions that work best with dense semantic retrieval.

### 🎯 Expected Outcome
1. In the `Overview` dashboard, if no documents are uploaded, show 3 sample cards explaining document types (e.g. Research Papers, Invoices/Contracts, Product Specs).
2. In the `Chat with Documents` view, enhance the suggested prompt pills to show category chips (e.g. `[Summary]`, `[Key Concepts]`, `[Data Extraction]`).

### ✅ Acceptance Criteria
- [ ] Does not clutter the UI when documents are already indexed.
- [ ] Clean modern design aligned with the midnight navy / electric cyan theme tokens.
- [ ] Clicking a suggested prompt pre-fills the chat input seamlessly.

---

## 💬 How to Propose New Ideas

Have an idea not listed here? Open a [Feature Request](https://github.com/Atharv428/DocuMind-AI/issues/new?template=feature_request.md) or start a conversation in our [GitHub Discussions](https://github.com/Atharv428/DocuMind-AI/discussions)!

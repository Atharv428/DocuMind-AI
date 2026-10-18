# Contributing to DocuMind AI

Thank you for your interest in contributing to **DocuMind AI**! We welcome contributions from developers, students, researchers, open-source maintainers, and AI engineers of all experience levels.

Whether you are fixing a typo, adding document loaders, optimizing RAG prompt templates, or expanding test coverage, your help makes DocuMind AI better for everyone.

> 💡 **Looking for a good place to start?**
> Check out our curated [Starter Issues Backlog](https://github.com/Atharv428/DocuMind-AI/blob/main/docs/STARTER_ISSUES.md) for small, beginner-friendly tasks!

---

## 🌟 Contribution Opportunities

We actively encourage contributions across multiple areas:
- **Beginner-Friendly Fixes**: Clearer error messages, expanded troubleshooting docs, improved empty states.
- **Document Ingestion**: Support for additional file formats (`.txt`, `.md`, `.docx`), OCR support for scanned documents using Tesseract.
- **RAG Pipeline Enhancements**: Query rewriting, semantic reranking, hybrid keyword/vector search (BM25 + embeddings).
- **LLM Synthesis & Streaming**: Token streaming with `st.write_stream`, customizable system prompts, multi-model benchmarking.
- **Test Suite Expansion**: Additional pytest test cases for chunking edge cases, vector store filtering, and malformed file handling.
- **UI & Accessibility**: Streamlit component polish, mobile view optimizations, keyboard shortcuts.

---

## 🛠️ Development Setup (Windows PowerShell)

DocuMind AI is developed with **Python 3.13+** on Windows. Follow these steps to set up your local development environment:

### 1. Fork and Clone the Repository

Fork the repository on GitHub by clicking the **Fork** button at [https://github.com/Atharv428/DocuMind-AI](https://github.com/Atharv428/DocuMind-AI).

Clone your fork locally:

```powershell
git clone https://github.com/<your-username>/DocuMind-AI.git
cd DocuMind-AI
```

### 2. Set Up a Virtual Environment

Create and activate a dedicated virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(Note: If PowerShell blocks script execution, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

*(On Linux / macOS: `python3 -m venv .venv && source .venv/bin/activate`)*

### 3. Install Dependencies

Upgrade pip and install all required packages:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the template environment file:

```powershell
Copy-Item .env.example .env
```

The default `.env` configuration is pre-tuned for local-first execution:
- `LLM_PROVIDER=ollama`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=llama3.2:1b`
- `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`
- `CHROMA_PATH=./data/chroma`

### 5. Start Ollama and Pull the Model

DocuMind AI utilizes Ollama for local LLM generation. Ensure Ollama is installed from [ollama.com](https://ollama.com/download) and running:

```powershell
ollama pull llama3.2:1b
```

Verify that the Ollama service is reachable by visiting `http://localhost:11434` or running:

```powershell
curl http://localhost:11434/api/tags
```

### 6. Launch the Application

Start the local Streamlit development server:

```powershell
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

*(If port 8501 is occupied by another process, run: `streamlit run app.py --server.port 8502`)*

---

## 🧪 Testing Guidelines

We require all pull requests to pass automated tests and syntax compilation before merging.

### 1. Run the Full Test Suite

```powershell
python -m pytest
```

All 21+ tests should pass:
```text
tests/test_chunker.py .
tests/test_document_loader.py .
tests/test_features_workflow.py .
tests/test_local_rag.py .
tests/test_ollama_generator.py .
tests/test_pipeline.py .
tests/test_retriever.py .
```

### 2. Verify Python Syntax

```powershell
python -m py_compile app.py rag/*.py services/*.py ui/*.py
```

### 3. Writing New Tests

- Place test files in the `tests/` directory named `test_<feature>.py`.
- Use `pytest` fixtures like `tmp_path` for temporary file creation.
- Never use real personal or sensitive documents in tests; use purely synthetic lorem-ipsum or mock data.

---

## 🌿 Branching & Development Workflow

1. **Keep Your Fork Synchronized**:
   ```bash
   git remote add upstream https://github.com/Atharv428/DocuMind-AI.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a Topic Branch**:
   Always work on a focused branch off `main`:
   ```bash
   git checkout -b feat/add-markdown-loader
   # or
   git checkout -b fix/ollama-timeout-handling
   ```

3. **Follow Code Style Expectations**:
   - Write clean, readable, modular Python code.
   - Use explicit type annotations (`from __future__ import annotations`, `list[dict]`, `str | None`).
   - Maintain separation of concerns:
     - `rag/`: Ingestion, chunking, embeddings, vector storage, and generation.
     - `services/`: Document registry and session state persistence.
     - `ui/`: CSS theme tokens and Streamlit component widgets.
     - `app.py`: Top-level application layout and view orchestration.
   - Preserve existing docstrings and comments.

4. **Commit with Conventional Commits**:
   ```bash
   git add <modified-files>
   git commit -m "feat(loader): add markdown file extraction support"
   ```
   Prefixes:
   - `feat:` New functionality
   - `fix:` Bug fix
   - `docs:` Documentation improvements
   - `refactor:` Code restructuring without functional changes
   - `test:` Adding or updating tests
   - `chore:` Tooling or dependency maintenance

---

## 🔒 Security & Privacy Rules (Strict)

When submitting contributions, you **must ensure**:
- **No Secrets**: Never commit `.env` files, API keys, tokens, or credentials.
- **No Private Documents**: Never commit private personal PDF documents or user ChromaDB databases.
- **Test Fixture Sanitization**: Any sample documents added to the repository must contain purely synthetic or public sample text.
- **Credential Masking**: Any code handling API keys must sanitize error messages with `[API_KEY_HIDDEN]`.

---

## 🚀 Pull Request Checklist

Before opening your pull request at [https://github.com/Atharv428/DocuMind-AI/pulls](https://github.com/Atharv428/DocuMind-AI/pulls), ensure:

- [ ] Code is developed on a dedicated feature branch (not on `main`).
- [ ] Python syntax passes: `python -m py_compile app.py rag/*.py services/*.py ui/*.py`.
- [ ] All automated tests pass: `python -m pytest`.
- [ ] Application launches cleanly in Streamlit without runtime errors.
- [ ] No private `.env` files or credentials are staged (`git status`).
- [ ] Conventional Commit message standards are followed.
- [ ] PR description clearly explains the motivation, changes made, and verification steps.

---

## 🤝 Community & Code of Conduct

- Be welcoming, respectful, and encouraging to all contributors.
- Provide constructive, supportive feedback during code reviews.
- Focus on user privacy, local-first performance, and codebase reliability.

Thank you for contributing to **DocuMind AI**!

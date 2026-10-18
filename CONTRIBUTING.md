# Contributing to DocuMind AI

Thank you for your interest in contributing to **DocuMind AI**! We welcome contributions from developers, researchers, open-source maintainers, and AI engineers of all experience levels.

This document outlines the guidelines and workflow for contributing to the project.

---

## 🌟 Types of Contributions Welcome

We actively encourage:
- **Bug Fixes**: Resolving issues with document parsing, chunking, retrieval, or UI edge cases.
- **New Features**: Expanding support for additional document formats (Markdown, DOCX, TXT), OCR support (Tesseract/PaddleOCR), or chat response streaming.
- **RAG & Prompt Optimizations**: Enhancing chunking strategies, retrieval reranking, or grounding prompts for local LLMs.
- **Documentation**: Improving guides, tutorials, setup walkthroughs, and inline code documentation.
- **Tests**: Expanding automated test coverage for retrieval accuracy, vector store operations, and pipeline fallbacks.

---

## 🛠️ Development Setup

### 1. Fork and Clone the Repository

Fork the repository on GitHub, then clone your fork locally:

```powershell
git clone https://github.com/<your-username>/DocuMind-AI.git
cd DocuMind-AI
```

### 2. Set Up a Virtual Environment

Ensure you are using **Python 3.13+**:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(On Linux / macOS: `python3 -m venv .venv && source .venv/bin/activate`)*

### 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure Local Environment

Copy the template configuration file:

```powershell
Copy-Item .env.example .env
```

Ensure Ollama is installed and running locally with the recommended model:

```powershell
ollama pull llama3.2:1b
```

### 5. Launch the Application

```powershell
streamlit run app.py
```

---

## 🌿 Branching Strategy & Workflow

1. **Create a Feature Branch**:
   Always branch off `main` with a descriptive name:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Develop and Test**:
   Make focused, modular changes. Ensure that all existing and new tests pass:
   ```powershell
   python -m pytest
   ```

3. **Check Code Formatting & Syntax**:
   Ensure Python files compile cleanly without syntax errors:
   ```powershell
   python -m py_compile app.py rag/*.py services/*.py ui/*.py
   ```

---

## 📝 Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` A new feature or capability
- `fix:` A bug fix
- `docs:` Documentation improvements
- `refactor:` Code restructuring without functional changes
- `test:` Adding or updating tests
- `chore:` Maintenance, dependency bumps, or tooling updates

**Example**:
```text
feat(rag): add support for semantic passage reranking
fix(loader): handle corrupted PDF headers gracefully
docs(readme): clarify Ollama installation steps for Windows
```

---

## 🔒 Security & Privacy Rules

When submitting contributions, you **must ensure**:
- **No Secrets**: Never commit `.env` files, API keys, tokens, or credentials.
- **No Private Data**: Never commit private PDF documents, personal notes, or proprietary files.
- **Sanitized Fixtures**: Any test documents added to the repository must contain purely synthetic, public, or lorem-ipsum content.
- **Sanitized Errors**: Exception handlers must never print raw API keys into logs or user-facing messages.

---

## 🚀 Submitting a Pull Request (PR)

1. **Push to Your Fork**:
   ```bash
   git push origin feat/your-feature-name
   ```

2. **Open a Pull Request**:
   - Go to `https://github.com/Atharv428/DocuMind-AI`
   - Click **Compare & pull request**
   - Fill out the PR template with a clear description of your changes, motivation, and test verification.

3. **Code Review**:
   - Maintainers will review your PR, suggest improvements, and run automated checks.
   - Address feedback constructively and keep commits focused.

---

## 🤝 Code of Conduct & Expectations

- Be respectful, constructive, and welcoming to all participants.
- Provide thoughtful feedback during code reviews.
- Focus on technical merit, maintainability, and user privacy.

Thank you for helping make DocuMind AI better for everyone!

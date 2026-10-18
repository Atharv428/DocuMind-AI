## 📌 Pull Request Overview
Provide a clear, high-level summary of what this Pull Request changes, adds, or fixes.

Closes #(issue number if applicable)

---

## 🛠️ Category of Change
- [ ] 🐛 Bug fix (non-breaking change which resolves a reported issue)
- [ ] ✨ New feature (non-breaking enhancement adding functionality)
- [ ] ⚡ Performance / RAG retrieval optimization
- [ ] 📝 Documentation & setup guide improvement
- [ ] 🧪 Testing & test suite expansion
- [ ] 🎨 UI & visual aesthetic enhancement

---

## 🧪 Verification & Testing Checklist
Please check all that apply:
- [ ] **Python Syntax**: All modified Python files compile cleanly (`python -m py_compile app.py rag/*.py services/*.py ui/*.py`)
- [ ] **Automated Tests**: Test suite passes without errors (`python -m pytest`)
- [ ] **Local Interface Tested**: Tested locally in Streamlit (`streamlit run app.py`)
- [ ] **Ollama Verified**: Verified with local Ollama (`llama3.2:1b`) or verified fallback behavior
- [ ] **Responsive UI**: Verified on desktop and narrower window viewports

---

## 🔒 Privacy & Clean Code Assurance
- [ ] **Zero Credentials**: Confirmed no `.env` files, API keys, tokens, or credentials are committed.
- [ ] **Zero Private Documents**: Confirmed no real personal PDF files or private ChromaDB indices are committed.
- [ ] **Test Fixtures**: Any added test files contain solely synthetic or mock text.
- [ ] **Clean Git History**: Commits follow [Conventional Commits](https://www.conventionalcommits.org/) standards.

---

## 📷 Screenshots / Visual Demos (if applicable)
Attach before/after screenshots or GIFs demonstrating UI enhancements.

# Security Policy

## 🔒 Supported Versions

The following table indicates the versions of **DocuMind AI** currently receiving security updates:

| Version | Supported          |
| :---    | :---               |
| 1.3.x   | :white_check_mark: |
| < 1.3   | :x:                |

---

## 🛡️ Reporting a Vulnerability

We take the security and privacy of DocuMind AI and its users seriously. If you discover a potential security vulnerability, credential leak risk, or privacy flaw:

1. **Do NOT open a public GitHub issue** with sensitive vulnerability details.
2. Please contact the project maintainer directly:
   - **Maintainer**: Atharv Kiran Nawale
   - **Email**: `athravnawale100@gmail.com`
   - **GitHub**: [@Atharv428](https://github.com/Atharv428)
3. Include detailed reproduction steps, potential impact, and suggested remediations where possible.
4. You will receive an acknowledgment within 48 hours, followed by regular updates until a patch is issued.

---

## 🏛️ Local-First Security Architecture

DocuMind AI is architected with a local-first philosophy:

- **Data Locality**: When operating in Ollama mode, all document parsing, text chunking, dense vector embedding generation, and LLM synthesis occur exclusively on the local machine.
- **Zero Third-Party Telemetry**: The application does not collect usage analytics, tracking cookies, or prompt telemetry.
- **Credential Masking**: Cloud provider keys (e.g., Google Gemini API keys) are sanitized in memory and substituted with `[API_KEY_HIDDEN]` across all stack traces, log outputs, and UI notifications.
- **Permanent Purge**: Deletion of documents via the Document Library immediately deletes physical files from `data/uploads` and removes all associated vectors from ChromaDB.

---

## ⚠️ Safe Usage Guidelines

- **Keep `.env` Private**: Never share your `.env` file or commit it to source control.
- **Verify Input Documents**: Only upload documents from trusted sources to prevent malicious PDF format exploitation.
- **Local Network Safety**: The default Streamlit server runs on `localhost:8501`. If exposing the port across a local network or VPN, ensure appropriate reverse-proxy authentication is configured.

from __future__ import annotations

import datetime
import hashlib
import html
from pathlib import Path

import streamlit as st

from rag.config import reload_settings, save_api_key_to_env, save_setting_to_env, settings
from rag.document_loader import build_document_record
from rag.pipeline import RAGPipeline
from services.chat_service import ChatService
from services.document_service import DocumentService
from ui.components import (
    render_citation_cards,
    render_empty_state,
    render_sidebar_footer,
    render_sidebar_navigation,
    render_stat_kpi_cards,
    render_top_bar,
)
from ui.styles import get_theme_css

# Page Configuration
st.set_page_config(
    page_title="DocuMind AI — Intelligent Document Workspace",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_theme_css(), unsafe_allow_html=True)


# ---------------- INITIALIZE SERVICES & STATE ----------------
if "pipeline" not in st.session_state:
    st.session_state.pipeline = RAGPipeline()
if "document_service" not in st.session_state or not hasattr(st.session_state.document_service, "get_document"):
    st.session_state.document_service = DocumentService()
if "chat_service" not in st.session_state or not hasattr(st.session_state.chat_service, "clear_empty_sessions"):
    st.session_state.chat_service = ChatService()

pipeline: RAGPipeline = st.session_state.pipeline
document_service: DocumentService = st.session_state.document_service
chat_service: ChatService = st.session_state.chat_service

uploaded_documents = document_service.list_documents()

# Navigation State
if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Overview"

# Chat Session State
if "session_id" not in st.session_state:
    sessions = chat_service.list_sessions()
    if sessions:
        st.session_state.session_id = sessions[-1]["session_id"]
    else:
        new_session = chat_service.create_session("New chat")
        st.session_state.session_id = new_session["session_id"]

chat_service.clear_empty_sessions(keep_session_id=st.session_state.session_id)

# Document Selection State
if "selected_doc_ids" not in st.session_state:
    st.session_state.selected_doc_ids = [doc["document_id"] for doc in uploaded_documents]
else:
    valid_ids = {doc["document_id"] for doc in uploaded_documents}
    st.session_state.selected_doc_ids = [
        did for did in st.session_state.selected_doc_ids if did in valid_ids
    ]

# Feature States
if "doc_summaries" not in st.session_state:
    st.session_state.doc_summaries = {}
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None
if "upload_status" not in st.session_state:
    st.session_state.upload_status = None
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "delete_confirm_id" not in st.session_state:
    st.session_state.delete_confirm_id = None

# Active Provider & Generation Status
current_provider = getattr(pipeline.generator, "provider", settings.llm_provider)
is_engine_ready = pipeline.generator.is_available()

if current_provider == "ollama":
    active_model_name = getattr(pipeline.generator.ollama, "model_name", settings.ollama_model)
    engine_label = f"Ollama ({active_model_name})"
    engine_subtext = "Local LLM • Offline" if is_engine_ready else "Ollama Offline"
elif current_provider == "gemini":
    active_model_name = getattr(pipeline.generator.gemini, "model_name", settings.gemini_model)
    engine_label = f"Gemini ({active_model_name})"
    engine_subtext = "Cloud AI Studio" if is_engine_ready else "API Key Needed"
else:
    active_model_name = "Cosine Retrieval"
    engine_label = "Local Retrieval"
    engine_subtext = "Zero LLM Required"

chunk_count = pipeline.vector_store.count()


def reset_session() -> None:
    session = chat_service.create_session("New chat")
    st.session_state.session_id = session["session_id"]
    st.session_state.messages = []


curr_session = chat_service.get_session(st.session_state.session_id)
st.session_state.messages = curr_session.get("messages", []) if curr_session else []


def persist_message(message: dict) -> None:
    chat_service.add_message(
        st.session_state.session_id,
        message["role"],
        message["content"],
        message.get("citations", []),
    )
    session_data = chat_service.get_session(st.session_state.session_id)
    st.session_state.messages = session_data.get("messages", []) if session_data else []


# ---------------- SIDEBAR ----------------
with st.sidebar:
    new_nav = render_sidebar_navigation(st.session_state.active_nav)
    if new_nav != st.session_state.active_nav:
        st.session_state.active_nav = new_nav
        st.rerun()

    # Document Selection Filter in Sidebar
    with st.expander("📄 Active Documents", expanded=False):
        if uploaded_documents:
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                if st.button("Select All", key="sb_sel_all", use_container_width=True):
                    st.session_state.selected_doc_ids = [d["document_id"] for d in uploaded_documents]
                    st.rerun()
            with col_sel2:
                if st.button("Clear All", key="sb_desel_all", use_container_width=True):
                    st.session_state.selected_doc_ids = []
                    st.rerun()

            for doc in uploaded_documents:
                doc_id = doc["document_id"]
                is_sel = doc_id in st.session_state.selected_doc_ids
                chk = st.checkbox(
                    doc["filename"],
                    key=f"sb_chk_{doc_id}",
                    value=is_sel,
                )
                if chk and doc_id not in st.session_state.selected_doc_ids:
                    st.session_state.selected_doc_ids.append(doc_id)
                    st.rerun()
                elif not chk and doc_id in st.session_state.selected_doc_ids:
                    st.session_state.selected_doc_ids.remove(doc_id)
                    st.rerun()
            st.caption(f"{len(st.session_state.selected_doc_ids)} of {len(uploaded_documents)} active")
        else:
            st.caption("No files indexed yet.")

    # Chat History in Sidebar
    with st.expander("🕒 Recent Chats", expanded=False):
        all_chats = chat_service.list_sessions()
        for chat_item in all_chats:
            sid = chat_item["session_id"]
            is_active_chat = (sid == st.session_state.session_id)
            chat_title = chat_item["title"]
            if is_active_chat:
                chat_title = f"👉 {chat_title}"

            c_btn, c_del = st.columns([4, 1])
            with c_btn:
                if st.button(chat_title, key=f"sb_chat_{sid}", use_container_width=True):
                    st.session_state.session_id = sid
                    st.session_state.active_nav = "Chat with Documents"
                    st.rerun()
            with c_del:
                if st.button("✖", key=f"sb_del_chat_{sid}", help="Delete chat"):
                    chat_service.delete_session(sid)
                    if st.session_state.session_id == sid:
                        rem = chat_service.list_sessions()
                        if rem:
                            st.session_state.session_id = rem[0]["session_id"]
                        else:
                            ns = chat_service.create_session("New chat")
                            st.session_state.session_id = ns["session_id"]
                    st.rerun()

        if st.button("➕ Start New Chat", key="sb_btn_new_chat", use_container_width=True, type="primary"):
            reset_session()
            st.session_state.active_nav = "Chat with Documents"
            st.rerun()

    # Footer
    render_sidebar_footer(
        provider_name=current_provider,
        model_name=active_model_name,
        is_engine_ready=is_engine_ready,
        doc_count=len(uploaded_documents),
        chunk_count=chunk_count,
    )


# ---------------- TOP BAR ----------------
render_top_bar(
    current_section=st.session_state.active_nav,
    doc_count=len(st.session_state.selected_doc_ids),
    provider_name=current_provider,
    model_name=active_model_name,
    is_engine_ready=is_engine_ready,
)


# ---------------- REUSABLE UPLOAD HANDLER ----------------
def render_upload_widget(key_prefix: str = "main") -> None:
    """Renders a modern, validated PDF upload dropzone with progress feedback."""
    if st.session_state.upload_status:
        st_type, st_msg = st.session_state.upload_status
        if st_type == "success":
            st.success(st_msg)
        elif st_type == "info":
            st.info(st_msg)
        elif st_type == "warning":
            st.warning(st_msg)
        else:
            st.error(st_msg)

    uploaded_file = st.file_uploader(
        "Upload PDF documents (Max 25 MB)",
        type=["pdf"],
        accept_multiple_files=False,
        key=f"{key_prefix}_file_uploader",
        help="Select a PDF document to parse, chunk, and index into ChromaDB vector store.",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_size_kb = len(file_bytes) / 1024
        col_up1, col_up2 = st.columns([3, 1])
        with col_up1:
            st.caption(f"Selected: **{uploaded_file.name}** ({file_size_kb:.1f} KB)")
        with col_up2:
            trigger_index = st.button("📥 Index Document", key=f"{key_prefix}_btn_index", type="primary", use_container_width=True)

        if trigger_index:
            # 1. Validations
            if len(file_bytes) == 0:
                st.session_state.upload_status = ("error", "The uploaded file is empty (0 bytes).")
                st.rerun()

            if not file_bytes.startswith(b"%PDF"):
                st.session_state.upload_status = ("error", "Invalid file: Missing standard '%PDF' file header.")
                st.rerun()

            max_bytes = settings.max_file_size_mb * 1024 * 1024
            if len(file_bytes) > max_bytes:
                st.session_state.upload_status = ("error", f"File size exceeds the {settings.max_file_size_mb} MB limit.")
                st.rerun()

            file_hash = hashlib.sha256(file_bytes).hexdigest()
            existing = document_service.find_by_hash(file_hash)
            if existing:
                st.session_state.upload_status = (
                    "info",
                    f"'{uploaded_file.name}' is already indexed in your knowledge base ({existing.get('page_count', 1)} pages).",
                )
                if file_hash not in st.session_state.selected_doc_ids:
                    st.session_state.selected_doc_ids.append(file_hash)
                st.rerun()

            target_path = settings.uploads_path / uploaded_file.name
            target_path.write_bytes(file_bytes)

            try:
                with st.spinner("Extracting text with PyMuPDF, generating local embeddings, and indexing into ChromaDB..."):
                    result = pipeline.index_document(str(target_path), document_id=file_hash)

                document_meta = {
                    "document_id": file_hash,
                    "filename": uploaded_file.name,
                    "file_size": target_path.stat().st_size,
                    "page_count": result["pages"],
                    "status": "Indexed",
                    "uploaded_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "hash": file_hash,
                }
                document_service.add_document(document_meta)

                if file_hash not in st.session_state.selected_doc_ids:
                    st.session_state.selected_doc_ids.append(file_hash)

                st.session_state.upload_status = (
                    "success",
                    f"Successfully indexed '{uploaded_file.name}' ({result['pages']} pages, {result['chunks']} chunks stored in ChromaDB).",
                )
                st.rerun()
            except Exception as exc:
                if target_path.exists():
                    try:
                        target_path.unlink()
                    except Exception:
                        pass
                st.session_state.upload_status = ("error", f"Indexing failed: {exc}")
                st.rerun()


# =========================================================
# VIEW 1: OVERVIEW DASHBOARD
# =========================================================
if st.session_state.active_nav == "Overview":
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-badge">Local-First AI Document Intelligence</div>
            <div class="hero-headline">Your Documents. Your Knowledge. Your AI.</div>
            <div class="hero-subtitle">Transform static documents into searchable intelligence and grounded answers using local vector retrieval and Ollama LLM generation.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Real KPI Cards
    render_stat_kpi_cards(
        doc_count=len(uploaded_documents),
        chunk_count=chunk_count,
        chat_count=len(chat_service.list_sessions()),
        engine_label=engine_label,
        engine_subtext=engine_subtext,
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Quick Action Columns
    col_dash1, col_dash2 = st.columns([3, 2])

    with col_dash1:
        st.subheader("📤 Quick Upload & Index")
        render_upload_widget(key_prefix="overview")

        st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
        st.subheader("📑 Recent Documents")
        if uploaded_documents:
            for doc in uploaded_documents[-4:]:
                doc_id = doc["document_id"]
                file_size_kb = doc.get("file_size", 0) / 1024

                col_d1, col_d2 = st.columns([4, 1])
                with col_d1:
                    st.markdown(
                        f"""
                        <div class="doc-item-card" style="margin-bottom: 0.5rem; padding: 0.75rem 1rem;">
                            <div>
                                <span style="font-weight: 600; color: var(--text-title); font-size: 0.92rem;">📄 {html.escape(doc['filename'])}</span>
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 2px;">
                                    {doc.get('page_count', 1)} page(s) • {file_size_kb:.1f} KB • Uploaded {doc.get('uploaded_at', '')}
                                </div>
                            </div>
                            <span class="source-badge">Indexed</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_d2:
                    if st.button("Chat", key=f"ov_chat_{doc_id}", use_container_width=True):
                        st.session_state.selected_doc_ids = [doc_id]
                        st.session_state.active_nav = "Chat with Documents"
                        st.rerun()
        else:
            render_empty_state(
                title="No documents uploaded yet",
                description="Upload your first PDF document to build your intelligent knowledge base.",
                icon_type="document",
            )

    with col_dash2:
        st.subheader("🚀 Getting Started")
        st.markdown(
            """
            <div class="surface-card">
                <div style="display: flex; gap: 12px; margin-bottom: 1rem;">
                    <div class="source-badge" style="height: 24px;">1</div>
                    <div>
                        <div style="font-weight: 600; color: var(--text-title); font-size: 0.92rem;">Upload Your PDFs</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.4;">Add documents up to 25MB. PyMuPDF extracts text preserving accurate 1-indexed page geometry.</div>
                    </div>
                </div>
                <div style="display: flex; gap: 12px; margin-bottom: 1rem;">
                    <div class="source-badge" style="height: 24px;">2</div>
                    <div>
                        <div style="font-weight: 600; color: var(--text-title); font-size: 0.92rem;">Dense Vector Search</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.4;">Sentence Transformers generate 384-dimensional dense embeddings stored locally in ChromaDB.</div>
                    </div>
                </div>
                <div style="display: flex; gap: 12px;">
                    <div class="source-badge" style="height: 24px;">3</div>
                    <div>
                        <div style="font-weight: 600; color: var(--text-title); font-size: 0.92rem;">Grounded AI Generation</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.4;">Ollama LLM synthesizes answers with authentic citations, zero external data leakage, and verifiable source references.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.subheader("⚡ System Capabilities")
        st.markdown(
            f"""
            <div class="surface-card" style="font-size: 0.85rem; color: var(--text-muted);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>Dense Embeddings</span>
                    <span style="color: var(--cyan); font-weight: 600;">all-MiniLM-L6-v2 (384-dim)</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>Vector Database</span>
                    <span style="color: #a78bfa; font-weight: 600;">ChromaDB (HNSW Cosine)</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>Active Generation Engine</span>
                    <span style="color: var(--success); font-weight: 600;">{html.escape(engine_label)}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>Offline Capability</span>
                    <span style="color: var(--text-title); font-weight: 600;">100% Fully Offline-Ready</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# VIEW 2: CHAT WITH DOCUMENTS
# =========================================================
elif st.session_state.active_nav == "Chat with Documents":
    st.subheader("💬 Chat with Documents")

    # Document Selection Quick Bar
    if uploaded_documents:
        col_c_sel, col_c_act = st.columns([4, 1.2])
        with col_c_sel:
            active_names = [d["filename"] for d in uploaded_documents if d["document_id"] in st.session_state.selected_doc_ids]
            if active_names:
                st.caption(f"Searching in: **{', '.join(active_names)}**")
            else:
                st.warning("⚠️ No documents selected! Please select documents in the sidebar or Document Library.")
        with col_c_act:
            if st.button("➕ New Chat", key="btn_chat_new", use_container_width=True):
                reset_session()
                st.rerun()

    # Welcome state if no messages
    suggested_query = None
    if not st.session_state.messages:
        st.markdown(
            """
            <div style="padding: 1.5rem 0 1rem 0;">
                <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-title); margin-bottom: 4px;">What would you like to explore today?</div>
                <div style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1.25rem;">Select a suggested prompt below or type your question in the composer.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        prompts = [
            "Summarize my document.",
            "What are the key findings?",
            "Explain the most important concepts.",
            "Find relevant information in my documents.",
            "Compare the main ideas across documents.",
        ]

        p_cols = st.columns(len(prompts))
        for idx, p in enumerate(prompts):
            with p_cols[idx]:
                if st.button(p, key=f"prompt_pill_{idx}", use_container_width=True):
                    suggested_query = p

    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("citations"):
                render_citation_cards(message["citations"])

    # Chat Input
    chat_query = st.chat_input("Ask a question about your documents (Enter to send)...")
    active_query = suggested_query or chat_query

    if active_query:
        if not uploaded_documents:
            st.warning("Please upload and index a PDF document before asking questions.")
        elif not st.session_state.selected_doc_ids:
            st.warning("No documents are currently selected. Please select at least one document from the sidebar.")
        else:
            user_msg = {"role": "user", "content": active_query, "citations": []}
            persist_message(user_msg)

            spinner_label = (
                f"Synthesizing grounded answer with {engine_label}..."
                if is_engine_ready
                else "Performing semantic passage search across local documents..."
            )

            with st.spinner(spinner_label):
                try:
                    response = pipeline.answer_question(
                        active_query,
                        selected_document_ids=list(st.session_state.selected_doc_ids),
                    )
                except Exception as exc:
                    response = {
                        "answer": f"Retrieval error occurred: {exc}",
                        "citations": [],
                    }

            assistant_msg = {
                "role": "assistant",
                "content": response["answer"],
                "citations": response.get("citations", []),
            }
            persist_message(assistant_msg)
            st.rerun()


# =========================================================
# VIEW 3: DOCUMENT LIBRARY
# =========================================================
elif st.session_state.active_nav == "Document Library":
    st.subheader("📁 Your Knowledge Base")
    st.caption("Manage, search, and explore your indexed documents.")

    with st.expander("📤 Add New Document to Knowledge Base", expanded=not bool(uploaded_documents)):
        render_upload_widget(key_prefix="lib_upload")

    if uploaded_documents:
        col_f1, col_f2, col_f3 = st.columns([3, 2, 1.5])
        with col_f1:
            search_query = st.text_input("🔍 Filter documents by filename", placeholder="Type to filter...", key="lib_filter_search")
        with col_f2:
            sort_by = st.selectbox("Sort by", ["Upload Date (Newest)", "Filename (A-Z)", "Page Count", "File Size"], key="lib_sort")
        with col_f3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Select All", key="lib_select_all", use_container_width=True):
                    st.session_state.selected_doc_ids = [d["document_id"] for d in uploaded_documents]
                    st.rerun()
            with col_b2:
                if st.button("Clear All", key="lib_clear_all", use_container_width=True):
                    st.session_state.selected_doc_ids = []
                    st.rerun()

        # Filter & Sort
        filtered_docs = [
            d for d in uploaded_documents
            if not search_query or search_query.lower() in d["filename"].lower()
        ]

        if sort_by == "Filename (A-Z)":
            filtered_docs.sort(key=lambda x: x["filename"].lower())
        elif sort_by == "Page Count":
            filtered_docs.sort(key=lambda x: x.get("page_count", 0), reverse=True)
        elif sort_by == "File Size":
            filtered_docs.sort(key=lambda x: x.get("file_size", 0), reverse=True)
        else:
            filtered_docs.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)

        st.caption(f"Displaying {len(filtered_docs)} of {len(uploaded_documents)} documents ({len(st.session_state.selected_doc_ids)} selected for search)")

        for doc in filtered_docs:
            doc_id = doc["document_id"]
            is_selected = doc_id in st.session_state.selected_doc_ids
            file_size_kb = doc.get("file_size", 0) / 1024

            col_chk, col_info, col_act = st.columns([0.4, 3.6, 2])
            with col_chk:
                chk = st.checkbox("Select", key=f"doclib_chk_{doc_id}", value=is_selected, label_visibility="collapsed")
                if chk and doc_id not in st.session_state.selected_doc_ids:
                    st.session_state.selected_doc_ids.append(doc_id)
                    st.rerun()
                elif not chk and doc_id in st.session_state.selected_doc_ids:
                    st.session_state.selected_doc_ids.remove(doc_id)
                    st.rerun()

            with col_info:
                st.markdown(
                    f"""
                    <div style="font-weight: 600; color: var(--text-title); font-size: 0.95rem;">
                        📄 {html.escape(doc['filename'])}
                        <span class="source-badge" style="margin-left: 8px;">{doc.get('status', 'Indexed')}</span>
                    </div>
                    <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 3px;">
                        {doc.get('page_count', 1)} page(s) • {file_size_kb:.1f} KB • Uploaded {doc.get('uploaded_at', 'Unknown')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_act:
                col_a1, col_a2, col_a3 = st.columns(3)
                with col_a1:
                    if st.button("Summary", key=f"lib_sum_{doc_id}", use_container_width=True):
                        st.session_state.active_nav = "Summaries"
                        st.session_state.selected_summary_doc = doc_id
                        st.rerun()
                with col_a2:
                    if st.button("Chat", key=f"lib_chat_{doc_id}", use_container_width=True):
                        st.session_state.selected_doc_ids = [doc_id]
                        st.session_state.active_nav = "Chat with Documents"
                        st.rerun()
                with col_a3:
                    if st.button("Delete", key=f"lib_del_{doc_id}", use_container_width=True):
                        st.session_state.delete_confirm_id = doc_id

            # Deletion Confirmation Guard
            if st.session_state.delete_confirm_id == doc_id:
                st.warning(f"Are you sure you want to delete '{doc['filename']}'? This will permanently remove its embeddings from ChromaDB.")
                col_c1, col_c2 = st.columns([1, 4])
                with col_c1:
                    if st.button("Yes, Delete", key=f"conf_del_{doc_id}", type="primary", use_container_width=True):
                        pipeline.vector_store.delete_document(doc_id)
                        document_service.delete_document(doc_id)
                        target_file = settings.uploads_path / doc["filename"]
                        if target_file.exists():
                            try:
                                target_file.unlink()
                            except Exception:
                                pass
                        if doc_id in st.session_state.selected_doc_ids:
                            st.session_state.selected_doc_ids.remove(doc_id)
                        st.session_state.delete_confirm_id = None
                        st.session_state.upload_status = ("info", f"Successfully deleted '{doc['filename']}'.")
                        st.rerun()
                with col_c2:
                    if st.button("Cancel", key=f"cancel_del_{doc_id}"):
                        st.session_state.delete_confirm_id = None
                        st.rerun()

            st.markdown("<hr style='margin: 0.5rem 0 0.75rem 0; border: none; border-top: 1px solid var(--border-subtle);'/>", unsafe_allow_html=True)
    else:
        render_empty_state(
            title="Knowledge Base is Empty",
            description="Upload PDF documents to begin building your searchable vector database.",
            icon_type="document",
        )


# =========================================================
# VIEW 4: SUMMARIES
# =========================================================
elif st.session_state.active_nav == "Summaries":
    st.subheader("📝 Document Summaries")
    st.caption("Generate executive briefs, key takeaways, and structural overviews.")

    if not uploaded_documents:
        render_empty_state(
            title="No documents to summarize",
            description="Upload a PDF in the Document Library before generating summaries.",
            icon_type="document",
        )
    else:
        doc_options = {d["document_id"]: d["filename"] for d in uploaded_documents}
        default_index = 0
        if "selected_summary_doc" in st.session_state and st.session_state.selected_summary_doc in doc_options:
            default_index = list(doc_options.keys()).index(st.session_state.selected_summary_doc)

        col_s1, col_s2, col_s3 = st.columns([3, 2, 1.5])
        with col_s1:
            chosen_doc_id = st.selectbox(
                "Select Document",
                options=list(doc_options.keys()),
                format_func=lambda did: doc_options[did],
                index=default_index,
                key="summary_doc_picker",
            )
        with col_s2:
            summary_format = st.selectbox(
                "Summary Format",
                ["Executive Brief (Concise)", "Key Findings & Action Items", "Comprehensive Breakdown"],
                key="summary_format_picker",
            )
        with col_s3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            run_summary_btn = st.button("Generate Summary", key="btn_run_summary", type="primary", use_container_width=True)

        chosen_doc = document_service.get_document(chosen_doc_id)
        if chosen_doc:
            if run_summary_btn or chosen_doc_id in st.session_state.doc_summaries:
                if run_summary_btn:
                    file_path = settings.uploads_path / chosen_doc["filename"]
                    if file_path.exists():
                        with st.spinner(f"Extracting and synthesizing summary for '{chosen_doc['filename']}'..."):
                            pages = build_document_record(file_path)["pages"]
                            full_text = "\n\n".join(p["text"] for p in pages)
                            summary_output = pipeline.summarize_document(full_text, title=chosen_doc["filename"])
                            st.session_state.doc_summaries[chosen_doc_id] = summary_output
                    else:
                        st.session_state.doc_summaries[chosen_doc_id] = "Error: Document file missing on disk."

                summary_text = st.session_state.doc_summaries.get(chosen_doc_id, "")

                st.markdown(
                    f"""
                    <div class="surface-card" style="margin-top: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.75rem;">
                            <span style="font-weight: 700; color: var(--text-title); font-size: 1.1rem;">📄 {chosen_doc['filename']}</span>
                            <span class="source-badge">{'AI Synthesized' if is_engine_ready else 'Extractive Overview (Local)'}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(summary_text)


# =========================================================
# VIEW 5: COMPARE DOCUMENTS
# =========================================================
elif st.session_state.active_nav == "Compare Documents":
    st.subheader("⚖️ Compare Documents")
    st.caption("Analyze similarities, differences, and unique takeaways across multiple sources.")

    if len(uploaded_documents) < 2:
        render_empty_state(
            title="Comparison requires at least 2 documents",
            description="Upload at least two PDF documents in your library to compare their concepts and data.",
            icon_type="document",
        )
    else:
        doc_map = {d["document_id"]: d["filename"] for d in uploaded_documents}
        selected_for_cmp = st.multiselect(
            "Select documents to compare",
            options=list(doc_map.keys()),
            format_func=lambda did: doc_map[did],
            default=list(doc_map.keys())[:2],
            key="cmp_doc_multiselect",
        )

        cmp_topic = st.text_input(
            "Comparison Focus (Optional)",
            value="What are the key similarities, differences, and unique takeaways?",
            key="cmp_topic_input",
        )

        if st.button("Run Document Comparison", key="btn_trigger_cmp", type="primary"):
            if len(selected_for_cmp) < 2:
                st.warning("Please select at least two documents.")
            else:
                with st.spinner("Analyzing document contexts across selected sources..."):
                    doc_summaries = []
                    for did in selected_for_cmp:
                        d_record = document_service.get_document(did)
                        if d_record:
                            fp = settings.uploads_path / d_record["filename"]
                            if fp.exists():
                                pgs = build_document_record(fp)["pages"]
                                txt = "\n\n".join(p["text"] for p in pgs)
                                doc_summaries.append(pipeline.summarize_document(txt, d_record["filename"]))

                    comparison_out = pipeline.compare_documents(cmp_topic, doc_summaries)
                    st.session_state.comparison_result = comparison_out

        if st.session_state.comparison_result:
            st.markdown(
                """
                <div class="surface-card" style="margin-top: 1.5rem;">
                    <div style="font-weight: 700; color: var(--text-title); font-size: 1.1rem; margin-bottom: 0.75rem;">
                        ⚖️ Comparative Analysis
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state.comparison_result)


# =========================================================
# VIEW 6: SEARCH DOCUMENTS
# =========================================================
elif st.session_state.active_nav == "Search Documents":
    st.subheader("🔍 Passage Semantic Search")
    st.caption("Search across all indexed passages in your local ChromaDB vector store.")

    if not uploaded_documents:
        render_empty_state(
            title="Vector store is empty",
            description="Upload and index documents to enable semantic vector retrieval.",
            icon_type="search",
        )
    else:
        col_sq, col_sk = st.columns([4, 1])
        with col_sq:
            search_query_text = st.text_input("Enter search phrase or question", placeholder="e.g. quarterly revenue growth, conclusion, technical specifications...", key="passage_search_q")
        with col_sk:
            search_top_k = st.slider("Top results", min_value=1, max_value=10, value=settings.top_k, key="passage_search_k")

        if search_query_text:
            with st.spinner("Computing query embeddings and searching ChromaDB..."):
                query_vec = pipeline.embedding_service.embed_query(search_query_text)
                hits = pipeline.retriever.retrieve(query_vec, top_k=search_top_k, document_filter=None)
                st.session_state.search_results = hits

        if st.session_state.search_results is not None:
            hits = st.session_state.search_results
            if not hits:
                st.info("No matching passages found for this search term.")
            else:
                st.markdown(f"**Found {len(hits)} matching passage(s):**")
                render_citation_cards(hits)


# =========================================================
# VIEW 7: SETTINGS
# =========================================================
elif st.session_state.active_nav == "Settings":
    st.subheader("⚙️ Settings & Configuration")
    st.caption("Manage AI providers, vector store parameters, and local privacy preferences.")

    tab_ai, tab_retrieval, tab_storage, tab_privacy = st.tabs([
        "🤖 AI Engine Configuration",
        "⚡ Retrieval Parameters",
        "💾 Storage & ChromaDB",
        "🔒 Privacy & Security",
    ])

    with tab_ai:
        st.markdown("**LLM Generation Provider**")
        st.caption("Choose which engine synthesizes answers from retrieved document passages.")

        provider_options = [
            ("ollama", "🦙 Ollama (Local LLM - Recommended & Local-First)"),
            ("gemini", "☁️ Google Gemini (Cloud API - Optional)"),
            ("retrieval_only", "🔍 Local Passage Retrieval Only (Zero LLM)"),
        ]

        provider_keys = [p[0] for p in provider_options]
        current_idx = provider_keys.index(current_provider) if current_provider in provider_keys else 0

        chosen_provider = st.radio(
            "Active Generation Provider",
            options=provider_keys,
            format_func=lambda k: dict(provider_options)[k],
            index=current_idx,
            key="stg_chosen_provider",
        )

        if chosen_provider != current_provider:
            pipeline.generator.set_provider(chosen_provider)
            save_setting_to_env("LLM_PROVIDER", chosen_provider)
            st.rerun()

        st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid var(--border-subtle);'/>", unsafe_allow_html=True)

        # Provider-specific configurations
        if chosen_provider == "ollama":
            st.markdown("**🦙 Ollama Local Settings**")
            st.caption("Connects directly to your local Ollama instance without sending documents outside your machine.")

            ollama_url_input = st.text_input(
                "Ollama Base URL",
                value=settings.ollama_base_url,
                key="stg_ollama_url",
                help="Default: http://localhost:11434",
            )

            # Discover installed Ollama models
            installed_models = pipeline.generator.ollama.list_models()
            default_model = settings.ollama_model
            if installed_models:
                if default_model not in installed_models and len(installed_models) > 0:
                    model_choices = installed_models
                else:
                    model_choices = installed_models
                model_idx = model_choices.index(default_model) if default_model in model_choices else 0
                chosen_ollama_model = st.selectbox(
                    "Installed Ollama Model",
                    options=model_choices,
                    index=model_idx,
                    key="stg_ollama_model_select",
                )
            else:
                chosen_ollama_model = st.text_input(
                    "Ollama Model Name",
                    value=settings.ollama_model,
                    key="stg_ollama_model_text",
                    help="e.g. llama3.2:1b, llama3.1:8b, mistral, etc.",
                )

            col_o1, col_o2 = st.columns(2)
            with col_o1:
                if st.button("🔍 Test Ollama Connection", key="btn_test_ollama", use_container_width=True):
                    pipeline.generator.ollama.set_base_url(ollama_url_input)
                    pipeline.generator.ollama.set_model(chosen_ollama_model)
                    ok, msg = pipeline.generator.ollama.check_access(test_call=True)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"⚠️ {msg}")

            with col_o2:
                if st.button("💾 Save Ollama Config", key="btn_save_ollama", use_container_width=True):
                    save_setting_to_env("OLLAMA_BASE_URL", ollama_url_input)
                    save_setting_to_env("OLLAMA_MODEL", chosen_ollama_model)
                    settings.ollama_base_url = ollama_url_input
                    settings.ollama_model = chosen_ollama_model
                    pipeline.generator.ollama.set_base_url(ollama_url_input)
                    pipeline.generator.ollama.set_model(chosen_ollama_model)
                    st.success("Ollama configuration saved to .env!")

        elif chosen_provider == "gemini":
            st.markdown("**☁️ Google Gemini API Settings**")
            st.caption("Enter a free API key from [Google AI Studio](https://aistudio.google.com/).")

            api_key_input = st.text_input(
                "Gemini API Key",
                value=settings.gemini_api_key,
                type="password",
                key="settings_gemini_key",
                help="Your API key is stored locally in .env and is masked in all logs.",
            )

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                if st.button("🔍 Verify Gemini Key", key="btn_settings_verify", use_container_width=True):
                    if not api_key_input.strip():
                        st.info("No API key configured.")
                    else:
                        pipeline.generator.gemini.set_api_key(api_key_input.strip())
                        is_ok, msg = pipeline.generator.gemini.check_access(test_call=True)
                        if is_ok:
                            st.success(f"✅ {msg}")
                        else:
                            st.warning(f"⚠️ {msg}")

            with col_t2:
                if st.button("💾 Save Gemini Key", key="btn_settings_save_env", use_container_width=True):
                    if save_api_key_to_env(api_key_input.strip()):
                        settings.gemini_api_key = api_key_input.strip()
                        pipeline.generator.gemini.set_api_key(api_key_input.strip())
                        st.success("Successfully saved GEMINI_API_KEY to .env!")
                    else:
                        st.error("Failed to write to .env file.")

            model_name_choice = st.selectbox(
                "Gemini Model",
                ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
                index=0 if settings.gemini_model == "gemini-2.0-flash" else 1,
                key="settings_model_choice",
            )
            if model_name_choice != settings.gemini_model:
                settings.gemini_model = model_name_choice
                pipeline.generator.gemini.set_model(model_name_choice)
                save_setting_to_env("GEMINI_MODEL", model_name_choice)

        else:
            st.info("Passage Retrieval Only mode is active. No LLM will be queried; answers will return exact matching passages with page citations.")

    with tab_retrieval:
        st.markdown("**Retrieval & Chunking Configuration**")
        st.caption("Customize how text is segmented and retrieved from the vector store.")

        settings.top_k = st.slider("Retrieval Top-K (Passages returned per query)", min_value=1, max_value=10, value=settings.top_k, key="stg_top_k")
        settings.chunk_size = st.slider("Chunk Size (Words per segment)", min_value=200, max_value=1200, value=settings.chunk_size, step=50, key="stg_chunk_size")
        settings.chunk_overlap = st.slider("Chunk Overlap (Words)", min_value=20, max_value=300, value=settings.chunk_overlap, step=10, key="stg_chunk_overlap")
        settings.temperature = st.slider("Generation Temperature", min_value=0.0, max_value=1.0, value=settings.temperature, step=0.05, key="stg_temperature")

    with tab_storage:
        st.markdown("**ChromaDB Vector Store**")
        st.caption("Local persistent embedded vectors and document records.")

        col_st1, col_st2 = st.columns(2)
        with col_st1:
            st.metric("Vector Database Status", "Online (Persistent)")
            st.metric("Total Indexed Chunks", f"{chunk_count:,}")
        with col_st2:
            st.metric("Storage Path", str(settings.chroma_path.name))
            st.metric("Embedding Model", "all-MiniLM-L6-v2 (384-dim)")

    with tab_privacy:
        st.markdown("**Privacy & Local Processing Guarantee**")
        st.markdown(
            """
            - **100% Local-First Pipeline**: Document parsing (PyMuPDF), chunking, and embedding generation (`sentence-transformers`) execute locally on your machine.
            - **Local Inference with Ollama**: When using Ollama, prompt synthesis and document generation run locally on your GPU/CPU with zero internet required.
            - **Zero Data Tracking**: Your documents, embeddings, and chat histories are never transmitted to third-party tracking services.
            - **Key Masking**: Any cloud API credentials are automatically masked as `[API_KEY_HIDDEN]` in logs, terminal outputs, and exceptions.
            - **Complete Data Purge**: Deleting a document removes its physical file from disk and deletes all associated embeddings from the ChromaDB collection.
            """
        )


# =========================================================
# VIEW 8: HELP & ABOUT
# =========================================================
elif st.session_state.active_nav == "Help & About":
    st.subheader("ℹ️ About DocuMind AI")
    st.caption("Local-First AI Document Intelligence & Grounded Question Answering")

    st.markdown(
        """
        <div class="surface-card" style="margin-bottom: 1.5rem;">
            <div style="font-weight: 700; color: var(--text-title); font-size: 1.15rem; margin-bottom: 0.5rem;">
                Architectural Design
            </div>
            <div style="font-size: 0.9rem; color: var(--text-muted); line-height: 1.6;">
                DocuMind AI is an offline-first RAG (Retrieval-Augmented Generation) application designed for privacy-preserving document intelligence. 
                It couples dense vector semantic search in ChromaDB with local LLM generation powered by Ollama, ensuring that your documents stay on your machine while delivering grounded, citeable answers.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("**Verified Technology Stack**")
        st.markdown(
            """
            - **Streamlit**: Modern reactive dashboard shell
            - **Ollama**: Local LLM generation (`llama3.2:1b`)
            - **PyMuPDF (`fitz`)**: Fast, accurate page text extraction with geometry preservation
            - **Sentence Transformers**: `all-MiniLM-L6-v2` dense vector representations
            - **ChromaDB**: Embedded vector database using HNSW indexing with cosine distance
            - **Google GenAI SDK**: Optional Gemini Cloud integration with billing-free fallback
            """
        )

    with col_h2:
        st.markdown("**Developer & Portfolio Information**")
        st.markdown(
            """
            - **Author**: Atharv Kiran Nawale
            - **GitHub**: [https://github.com/Atharv428](https://github.com/Atharv428)
            - **Repository**: DocuMind AI
            - **Architecture**: Modular RAG (Ingestion → Chunking → Embeddings → ChromaDB → Ollama Synthesis)
            - **License**: MIT License
            """
        )

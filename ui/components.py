from __future__ import annotations

import html
from typing import Any

import streamlit as st

from rag.config import settings


def render_brand_header() -> None:
    """Renders the top branding header in the sidebar."""
    st.sidebar.markdown(
        """
        <div class="brand-header">
            <div class="brand-logo-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                    <line x1="9" y1="7" x2="15" y2="7"></line>
                    <line x1="9" y1="11" x2="13" y2="11"></line>
                </svg>
            </div>
            <div class="brand-text-wrap">
                <span class="brand-title">DocuMind AI</span>
                <span class="brand-subtitle">Document Intelligence</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation(active_tab: str) -> str:
    """Renders the sidebar navigation tree and returns the selected item."""
    render_brand_header()

    st.sidebar.markdown('<div class="nav-category">WORKSPACE</div>', unsafe_allow_html=True)

    nav_items_workspace = [
        ("Overview", "📊 Overview"),
        ("Chat with Documents", "💬 Chat with Documents"),
        ("Document Library", "📁 Document Library"),
        ("Summaries", "📝 Summaries"),
        ("Compare Documents", "⚖️ Compare Documents"),
    ]

    selected_nav = active_tab
    for key, label in nav_items_workspace:
        is_active = (active_tab == key)
        btn_kind = "primary" if is_active else "secondary"
        if st.sidebar.button(label, key=f"nav_btn_{key}", use_container_width=True, type=btn_kind):
            selected_nav = key

    st.sidebar.markdown('<div class="nav-category">EXPLORATION</div>', unsafe_allow_html=True)
    nav_items_explore = [
        ("Search Documents", "🔍 Passage Search"),
    ]
    for key, label in nav_items_explore:
        is_active = (active_tab == key)
        btn_kind = "primary" if is_active else "secondary"
        if st.sidebar.button(label, key=f"nav_btn_{key}", use_container_width=True, type=btn_kind):
            selected_nav = key

    st.sidebar.markdown('<div class="nav-category">PREFERENCES</div>', unsafe_allow_html=True)
    nav_items_prefs = [
        ("Settings", "⚙️ Settings"),
        ("Help & About", "ℹ️ Help & About"),
    ]
    for key, label in nav_items_prefs:
        is_active = (active_tab == key)
        btn_kind = "primary" if is_active else "secondary"
        if st.sidebar.button(label, key=f"nav_btn_{key}", use_container_width=True, type=btn_kind):
            selected_nav = key

    return selected_nav


def render_sidebar_footer(
    provider_name: str,
    model_name: str,
    is_engine_ready: bool,
    doc_count: int,
    chunk_count: int,
) -> None:
    """Renders the connection status, workspace info, and version at bottom of sidebar."""
    st.sidebar.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)

    if provider_name == "ollama":
        if is_engine_ready:
            pill_class = "status-pill-ollama"
            status_text = f"Ollama ({model_name})"
        else:
            pill_class = "status-pill-warning"
            status_text = "Ollama Offline"
    elif provider_name == "gemini":
        if is_engine_ready:
            pill_class = "status-pill-gemini"
            status_text = f"Gemini ({model_name})"
        else:
            pill_class = "status-pill-warning"
            status_text = "Gemini Key Required"
    else:
        pill_class = "status-pill-local"
        status_text = "Local Passage Retrieval"

    st.sidebar.markdown(
        f"""
        <div class="status-pill {pill_class}" style="width: 100%; justify-content: center; margin-bottom: 8px;">
            <span class="status-dot"></span> {html.escape(status_text)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        f"""
        <div class="workspace-badge" style="justify-content: space-between; margin-bottom: 6px;">
            <span>🏢 Workspace</span>
            <span style="color: var(--text-title); font-weight: 600;">Local-First</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--text-dim); padding: 0 4px;">
            <span>DocuMind AI v1.3</span>
            <span>{doc_count} docs • {chunk_count:,} chunks</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_bar(
    current_section: str,
    doc_count: int,
    provider_name: str,
    model_name: str,
    is_engine_ready: bool,
) -> None:
    """Renders the sleek top navigation bar with breadcrumbs and system badges."""
    if provider_name == "ollama":
        badge_html = (
            f'<span class="status-pill status-pill-ollama"><span class="status-dot"></span> Ollama: {html.escape(model_name)}</span>'
            if is_engine_ready
            else '<span class="status-pill status-pill-warning"><span class="status-dot"></span> Ollama Offline</span>'
        )
    elif provider_name == "gemini":
        badge_html = (
            f'<span class="status-pill status-pill-gemini"><span class="status-dot"></span> Gemini: {html.escape(model_name)}</span>'
            if is_engine_ready
            else '<span class="status-pill status-pill-warning"><span class="status-dot"></span> Gemini Key Missing</span>'
        )
    else:
        badge_html = '<span class="status-pill status-pill-local"><span class="status-dot"></span> Local Passage Search</span>'

    st.markdown(
        f"""
        <div class="top-navbar">
            <div class="breadcrumb-wrap">
                <span>DocuMind AI</span>
                <span>/</span>
                <span class="breadcrumb-active">{html.escape(current_section)}</span>
            </div>
            <div class="topbar-actions">
                <span style="font-size: 0.8rem; color: var(--text-muted);">{doc_count} active document{'s' if doc_count != 1 else ''}</span>
                {badge_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_kpi_cards(
    doc_count: int,
    chunk_count: int,
    chat_count: int,
    engine_label: str,
    engine_subtext: str = "Local Engine",
) -> None:
    """Renders 4 high-impact SaaS KPI cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Documents</div>
                <div class="metric-value">{doc_count}</div>
                <div class="metric-subtext">📄 In knowledge base</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Vector Chunks</div>
                <div class="metric-value">{chunk_count:,}</div>
                <div class="metric-subtext">⚡ ChromaDB dense vectors</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Chat Sessions</div>
                <div class="metric-value">{chat_count}</div>
                <div class="metric-subtext">💬 Persisted threads</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">AI Engine</div>
                <div class="metric-value" style="font-size: 1.22rem; font-weight: 700; padding-top: 0.25rem;">{html.escape(engine_label)}</div>
                <div class="metric-subtext">🤖 {html.escape(engine_subtext)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_citation_cards(citations: list[dict]) -> None:
    """Renders expandable cited source cards with clean typography and badges."""
    if not citations:
        return
    st.markdown("**📑 Grounded Source Passages & Citations:**")
    for idx, citation in enumerate(citations, 1):
        filename = html.escape(str(citation.get("filename", "Unknown Document")))
        page_number = citation.get("page_number", "?")
        text = html.escape(str(citation.get("text", "")).strip())
        chunk_idx = citation.get("chunk_index", idx)
        distance = citation.get("distance")

        distance_badge = ""
        if distance is not None:
            try:
                dist_val = float(distance)
                # Cosine distance: smaller distance means higher relevance
                relevance_pct = max(0, min(100, int((1.0 - dist_val) * 100)))
                distance_badge = f'<span class="source-distance-badge">Relevance: {relevance_pct}%</span>'
            except (ValueError, TypeError):
                pass

        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-card-header">
                    <span class="source-filename">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                        </svg>
                        {filename}
                    </span>
                    <div style="display: flex; gap: 6px; align-items: center;">
                        <span class="source-badge">Page {page_number}</span>
                        <span class="source-badge" style="background: rgba(255,255,255,0.06); color: var(--text-dim); border-color: transparent;">Chunk {chunk_idx}</span>
                        {distance_badge}
                    </div>
                </div>
                <div class="citation-body">{text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_empty_state(
    title: str,
    description: str,
    icon_type: str = "document",
    action_label: str | None = None,
    action_key: str | None = None,
) -> bool:
    """Renders a modern empty state container with an optional action button."""
    svg_icon = """
    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="12" y1="18" x2="12" y2="12"></line>
        <line x1="9" y1="15" x2="15" y2="15"></line>
    </svg>
    """
    if icon_type == "search":
        svg_icon = """
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        """
    elif icon_type == "chat":
        svg_icon = """
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        """

    st.markdown(
        f"""
        <div class="empty-state-box">
            {svg_icon}
            <div class="empty-state-title">{html.escape(title)}</div>
            <div class="empty-state-desc">{html.escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if action_label and action_key:
        _, col, _ = st.columns([1, 1, 1])
        with col:
            return st.button(action_label, key=action_key, use_container_width=True, type="primary")
    return False

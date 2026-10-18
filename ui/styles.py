from __future__ import annotations


def get_theme_css() -> str:
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {
            --bg-base: #06090f;
            --bg-surface: #0a0f1d;
            --bg-surface-elevated: #0e1526;
            --bg-card: #111a2e;
            --bg-card-hover: #16223b;
            --bg-card-active: #1b2a4a;
            
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-medium: rgba(255, 255, 255, 0.14);
            --border-accent: rgba(99, 102, 241, 0.45);
            --border-cyan: rgba(56, 189, 248, 0.4);
            
            --primary: #6366f1;
            --primary-light: #818cf8;
            --primary-glow: rgba(99, 102, 241, 0.2);
            --cyan: #38bdf8;
            --cyan-glow: rgba(56, 189, 248, 0.16);
            --violet: #a855f7;
            --violet-glow: rgba(168, 85, 247, 0.18);
            
            --text-title: #f8fafc;
            --text-body: #e2e8f0;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.16);
            --warning: #f59e0b;
            --warning-glow: rgba(245, 158, 11, 0.16);
            --danger: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.16);
            
            --radius-xs: 4px;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
            
            --shadow-subtle: 0 4px 16px rgba(0, 0, 0, 0.35);
            --shadow-card: 0 8px 30px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 24px rgba(99, 102, 241, 0.22);
            --shadow-cyan-glow: 0 0 24px rgba(56, 189, 248, 0.2);
        }

        /* Global Reset & Typography */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            letter-spacing: -0.012em;
            color: var(--text-body);
        }

        code, pre, .font-mono {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* App Background */
        .stApp {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(ellipse 90% 55% at 50% -20%, rgba(99, 102, 241, 0.13), transparent),
                radial-gradient(ellipse 70% 45% at 100% 10%, rgba(56, 189, 248, 0.08), transparent),
                radial-gradient(ellipse 60% 40% at 0% 90%, rgba(168, 85, 247, 0.05), transparent);
            background-attachment: fixed;
            color: var(--text-body);
        }

        /* Main Container */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1280px !important;
        }

        /* Top Header Styling */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Sleek Modern Scrollbar */
        ::-webkit-scrollbar {
            width: 7px;
            height: 7px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.14);
            border-radius: 999px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.24);
        }

        /* SIDEBAR STYLING */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-surface) !important;
            border-right: 1px solid var(--border-subtle) !important;
            box-shadow: 6px 0 30px rgba(0, 0, 0, 0.5);
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 1.25rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Branding Block */
        .brand-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0.25rem 0.25rem 1.15rem 0.25rem;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid var(--border-subtle);
        }
        .brand-logo-icon {
            width: 40px;
            height: 40px;
            border-radius: var(--radius-md);
            background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 18px rgba(99, 102, 241, 0.45);
            color: #ffffff;
            font-weight: 700;
        }
        .brand-text-wrap {
            display: flex;
            flex-direction: column;
        }
        .brand-title {
            color: var(--text-title);
            font-size: 1.18rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            line-height: 1.2;
            background: linear-gradient(135deg, #ffffff 30%, #c7d2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-subtitle {
            color: var(--cyan);
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        /* Category Label */
        .nav-category {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: var(--text-dim);
            margin-top: 1rem;
            margin-bottom: 0.45rem;
            padding-left: 0.5rem;
        }

        /* Navigation Buttons */
        .stButton > button[kind="secondary"],
        .stButton > button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            border: 1px solid transparent !important;
            color: var(--text-muted) !important;
            text-align: left !important;
            justify-content: flex-start !important;
            border-radius: var(--radius-md) !important;
            padding: 0.55rem 0.85rem !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            transition: all 0.18s ease-in-out !important;
            width: 100% !important;
        }
        .stButton > button[kind="secondary"]:hover,
        .stButton > button[data-testid="baseButton-secondary"]:hover {
            background-color: var(--bg-card-hover) !important;
            color: var(--text-title) !important;
            border-color: var(--border-subtle) !important;
            transform: translateX(2px);
        }

        /* Active Navigation Item Override */
        .stButton > button[kind="primary"],
        .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.28) 0%, rgba(56, 189, 248, 0.18) 100%) !important;
            border: 1px solid var(--border-accent) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: var(--radius-md) !important;
            padding: 0.55rem 0.85rem !important;
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25) !important;
            text-align: left !important;
            justify-content: flex-start !important;
            width: 100% !important;
        }

        /* TOP NAVIGATION BAR */
        .top-navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(10, 15, 29, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 0.8rem 1.35rem;
            margin-bottom: 1.6rem;
            box-shadow: var(--shadow-subtle);
        }
        .breadcrumb-wrap {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.86rem;
            color: var(--text-dim);
        }
        .breadcrumb-active {
            color: var(--text-title);
            font-weight: 600;
            font-size: 0.94rem;
        }
        .topbar-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        /* STATUS PILLS & BADGES */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        .status-pill-ollama {
            background: var(--success-glow);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }
        .status-pill-gemini {
            background: var(--cyan-glow);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.35);
        }
        .status-pill-local {
            background: var(--primary-glow);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.35);
        }
        .status-pill-warning {
            background: var(--warning-glow);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.35);
        }
        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: currentColor;
            display: inline-block;
            box-shadow: 0 0 8px currentColor;
        }

        /* SURFACE & CARDS */
        .surface-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.35rem;
            box-shadow: var(--shadow-card);
            transition: all 0.22s ease;
        }
        .surface-card:hover {
            border-color: var(--border-medium);
        }

        /* KPI STAT CARDS */
        .metric-card {
            background: linear-gradient(180deg, rgba(17, 26, 46, 0.95) 0%, rgba(11, 17, 31, 0.95) 100%);
            border: 1px solid var(--border-subtle);
            border-top: 2px solid var(--primary);
            border-radius: var(--radius-lg);
            padding: 1.25rem 1.15rem;
            box-shadow: var(--shadow-subtle);
            position: relative;
            overflow: hidden;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: var(--border-accent);
            box-shadow: var(--shadow-card);
        }
        .metric-label {
            color: var(--text-dim);
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.45rem;
        }
        .metric-value {
            color: var(--text-title);
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: -0.035em;
            line-height: 1.1;
        }
        .metric-subtext {
            color: var(--text-muted);
            font-size: 0.78rem;
            margin-top: 0.45rem;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* HERO BANNER */
        .hero-banner {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(56, 189, 248, 0.08) 50%, rgba(14, 21, 38, 0.8) 100%);
            border: 1px solid var(--border-accent);
            border-radius: var(--radius-xl);
            padding: 2.25rem 2.25rem;
            margin-bottom: 1.85rem;
            position: relative;
            box-shadow: var(--shadow-glow);
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid var(--border-accent);
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--primary-light);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.85rem;
        }
        .hero-headline {
            font-size: 2.25rem;
            font-weight: 800;
            color: var(--text-title);
            letter-spacing: -0.035em;
            margin-bottom: 0.6rem;
            line-height: 1.2;
            background: linear-gradient(135deg, #ffffff 40%, #c7d2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: var(--text-muted);
            max-width: 680px;
            line-height: 1.55;
            margin-bottom: 1.25rem;
        }

        /* CITATION & PASSAGE CARDS */
        .source-card {
            background: rgba(14, 21, 38, 0.9);
            border: 1px solid var(--border-subtle);
            border-left: 3px solid var(--cyan);
            border-radius: var(--radius-md);
            padding: 1.1rem 1.35rem;
            margin-top: 0.85rem;
            margin-bottom: 0.85rem;
            transition: all 0.2s ease;
        }
        .source-card:hover {
            background: rgba(19, 30, 54, 0.98);
            border-color: var(--border-cyan);
            transform: translateX(2px);
        }
        .source-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.65rem;
            flex-wrap: wrap;
            gap: 6px;
        }
        .source-filename {
            font-size: 0.9rem;
            font-weight: 600;
            color: #93c5fd;
            display: flex;
            align-items: center;
            gap: 7px;
        }
        .source-badge {
            background: rgba(99, 102, 241, 0.2);
            color: #c7d2fe;
            border: 1px solid rgba(99, 102, 241, 0.4);
            border-radius: var(--radius-xs);
            padding: 2px 9px;
            font-size: 0.74rem;
            font-weight: 600;
        }
        .source-distance-badge {
            background: rgba(56, 189, 248, 0.15);
            color: #7dd3fc;
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: var(--radius-xs);
            padding: 2px 8px;
            font-size: 0.72rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }
        .citation-body {
            color: #cbd5e1;
            font-size: 0.89rem;
            line-height: 1.65;
            white-space: pre-wrap;
            word-break: break-word;
        }

        /* DOCUMENT ROW ITEM */
        .doc-item-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.18s ease;
        }
        .doc-item-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--border-medium);
        }

        /* EMPTY STATES */
        .empty-state-box {
            text-align: center;
            padding: 3.25rem 1.75rem;
            background: rgba(14, 21, 38, 0.5);
            border: 1px dashed var(--border-medium);
            border-radius: var(--radius-xl);
            margin: 1.5rem 0;
        }
        .empty-state-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--text-title);
            margin-top: 0.9rem;
            margin-bottom: 0.4rem;
        }
        .empty-state-desc {
            font-size: 0.9rem;
            color: var(--text-dim);
            max-width: 440px;
            margin: 0 auto 1.35rem auto;
            line-height: 1.55;
        }

        /* SIDEBAR FOOTER PROFILE */
        .sidebar-footer {
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-subtle);
        }
        .workspace-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-muted);
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.4rem 0.6rem;
            border-radius: var(--radius-sm);
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-subtle);
        }

        /* FORM CONTROLS OVERRIDES */
        div[data-baseweb="input"] {
            background-color: #0b1120 !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-body) !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px var(--primary-glow) !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #0b1120 !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-body) !important;
        }

        div[data-testid="stExpander"] {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            margin-bottom: 0.75rem !important;
        }
        div[data-testid="stExpander"]:hover {
            border-color: var(--border-medium) !important;
        }

        div[data-testid="stChatInput"] > div {
            background-color: #0b1120 !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: var(--radius-lg) !important;
        }
        div[data-testid="stChatInput"] > div:focus-within {
            border-color: var(--cyan) !important;
            box-shadow: 0 0 0 2px var(--cyan-glow) !important;
        }
    </style>
    """

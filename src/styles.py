"""
CSS personalizado para la interfaz Tech-Minimalist / Dark Academia.
Se inyecta via st.markdown(..., unsafe_allow_html=True).
"""

CUSTOM_CSS = """
<style>
/* ── Importar fuente premium ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* ── Variables de diseño ───────────────────────────────────────────────── */
:root {
    --bg-primary:    #121212;
    --bg-secondary:  #1C1C1E;
    --bg-card:       #1E1E21;
    --accent:        #4A90D9;
    --accent-soft:   rgba(74, 144, 217, 0.12);
    --text-primary:  #E0E0E0;
    --text-muted:    #888899;
    --border:        rgba(255, 255, 255, 0.07);
    --shadow:        0 2px 16px rgba(0, 0, 0, 0.45);
    --radius:        10px;
}

/* ── Fuente global ─────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}

/* ── Ocultar elementos de Streamlit UI ─────────────────────────────────── */
/* Menú hamburguesa */
#MainMenu                        { visibility: hidden; }
/* Botón Deploy */
.stDeployButton                  { display: none !important; }
/* Footer "Made with Streamlit" */
footer                           { visibility: hidden; }
/* Header decorativo de la app */
header[data-testid="stHeader"]   { background: transparent !important; }

/* ── Área principal ────────────────────────────────────────────────────── */
.main .block-container {
    background: var(--bg-primary);
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* ── Sidebar ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container {
    background: var(--bg-secondary) !important;
}

/* ── Burbujas de chat — usuario ────────────────────────────────────────── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 0.75rem;
    padding: 0.75rem 1rem;
}

/* ── Burbujas de chat — asistente ──────────────────────────────────────── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #1A2130 0%, #1C1C1E 100%);
    border: 1px solid rgba(74, 144, 217, 0.2);
    border-radius: var(--radius);
    box-shadow: var(--shadow), 0 0 0 1px rgba(74, 144, 217, 0.05);
    margin-bottom: 0.75rem;
    padding: 0.75rem 1rem;
}

/* ── Input de chat ─────────────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-soft) !important;
}

/* ── Expander de fuentes ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Botones ───────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-soft) !important;
    color: var(--accent) !important;
}

/* ── Botones de preguntas sugeridas (clase específica) ─────────────────── */
.suggested-btn > button {
    background: transparent !important;
    border: 1px solid rgba(74, 144, 217, 0.25) !important;
    color: var(--text-muted) !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 0.8rem !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
}
.suggested-btn > button:hover {
    background: var(--accent-soft) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── Títulos ───────────────────────────────────────────────────────────── */
h1 { font-weight: 600 !important; letter-spacing: -0.5px !important; }
h2, h3 { font-weight: 500 !important; }

/* ── Caption / texto secundario ────────────────────────────────────────── */
.stCaption { color: var(--text-muted) !important; }

/* ── Divider ───────────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar       { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
"""

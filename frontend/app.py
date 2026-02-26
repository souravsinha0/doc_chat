import uuid
from datetime import date, datetime

import requests
import streamlit as st

FASTAPI_URL = "http://localhost:8000"

# ────────────────────────────────────────────────
# Configurable Constants
# ────────────────────────────────────────────────
MAX_UPLOAD_FILES_PER_BATCH = 30  # Maximum number of files allowed in a single upload batch (configurable)

st.set_page_config(page_title="Velocis AI Assistant", layout="wide", page_icon="🤖")

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

    :root {
        --bg-primary: #07090f;
        --bg-secondary: #0d1117;
        --bg-card: #111827;
        --bg-card-hover: #141f2e;
        --border: #1e2d45;
        --border-bright: #2a3f5f;
        --accent: #3b82f6;
        --accent-dim: #1d4ed8;
        --accent-glow: rgba(59,130,246,0.15);
        --accent-subtle: rgba(59,130,246,0.08);
        --text-primary: #f0f4ff;
        --text-secondary: #8b9ab5;
        --text-muted: #4a5878;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --danger-subtle: rgba(239,68,68,0.08);
    }

    * { font-family: 'DM Sans', sans-serif; }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stHeader"] { height: 0rem !important; display: none !important; }
    .block-container { padding-top: 1.5rem !important; max-width: 100% !important; }

    /* ── Typography ── */
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.02em; }

    /* ── Sidebar & panels ── */
    .st-key-docs_panel, .st-key-history_panel {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }

    /* ── Header bar ── */
    .header-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 1.2rem;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .header-bar h2 {
        margin: 0;
        font-size: 1.15rem;
        color: var(--text-primary);
        font-weight: 700;
    }
    .header-bar .username-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    .header-brand {
        font-family: 'Syne', sans-serif;
        font-size: 1.25rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.03em;
    }

    /* ── Section titles ── */
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-muted);
        padding: 0 0 0.5rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 0.75rem;
    }

    /* ── File type badge ── */
    .file-type-badge {
        display: inline-block;
        font-size: 0.55rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        padding: 1px 5px;
        border-radius: 4px;
        background: var(--accent-subtle);
        color: var(--accent);
        border: 1px solid rgba(59,130,246,0.2);
        margin-top: 1px;
        vertical-align: middle;
    }

    /* ── Doc list row ── */
    .doc-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.3rem 0.4rem;
        border-radius: 6px;
        gap: 0.4rem;
        transition: background 0.15s;
    }
    .doc-row:hover { background: var(--bg-card-hover); }
    .doc-row-left {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        min-width: 0;
        flex: 1;
    }
    .doc-filename {
        font-size: 0.78rem;
        color: #c8d6f0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
    }

    /* ── Delete button — danger ghost style ── */
    [class*="del_"] button, [data-testid*="del_"] button {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-muted) !important;
        border-radius: 6px !important;
        padding: 0.15rem 0.35rem !important;
        font-size: 0.75rem !important;
        min-height: unset !important;
        height: 1.6rem !important;
        transition: background 0.15s, border-color 0.15s, color 0.15s !important;
    }
    [class*="del_"] button:hover, [data-testid*="del_"] button:hover {
        background: var(--danger-subtle) !important;
        border-color: rgba(239,68,68,0.35) !important;
        color: #ef4444 !important;
    }

    /* ── Chat bubbles ── */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 0.25rem 0 !important;
    }

    /* ── Inputs & textareas ── */
    [data-testid="stChatInput"] > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-bright) !important;
        border-radius: 12px !important;
        transition: border-color 0.2s;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }
    input[type="text"], input[type="password"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    input[type="text"]:focus, input[type="password"]:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    /* ── Buttons ── */
    [data-testid="stBaseButton-primary"] button,
    button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        letter-spacing: 0.01em;
        transition: opacity 0.2s, transform 0.15s !important;
    }
    [data-testid="stBaseButton-primary"] button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

    [data-testid="stBaseButton-secondary"] button,
    button[kind="secondary"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-bright) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-family: 'DM Sans', sans-serif !important;
        transition: background 0.2s, border-color 0.2s !important;
    }
    [data-testid="stBaseButton-secondary"] button:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--accent) !important;
        color: var(--text-primary) !important;
    }

    /* ── Checkboxes ── */
    [data-testid="stCheckbox"] label {
        font-size: 0.8rem !important;
        color: var(--text-secondary) !important;
    }

    /* ── Divider ── */
    hr { border-color: var(--border) !important; margin: 0.6rem 0 !important; }

    /* ── Alerts ── */
    [data-testid="stAlert"] {
        border-radius: 8px !important;
        font-size: 0.82rem !important;
    }

    /* ── Tabs (login) ── */
    [data-testid="stTabs"] button {
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
    }

    /* ── Login card ── */
    .login-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem 2.25rem;
    }

    /* ── Caption ── */
    [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        text-align: center;
    }

    /* ── Spinner ── */
    [data-testid="stSpinner"] { color: var(--accent) !important; }

    /* ── Scrollbars ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""",
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────
# Session state initialization
# ────────────────────────────────────────────────
if "initialized" not in st.session_state:
    token = st.query_params.get("token")
    username = st.query_params.get("user")

    if token and username:
        st.session_state.authenticated = True
        st.session_state.token = token
        st.session_state.username = username
    else:
        st.session_state.authenticated = False
        st.session_state.token = None
        st.session_state.username = None

    st.session_state.initialized = True
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.chat_messages = []
    st.session_state.uploaded_docs = []
    st.session_state.selected_doc_ids = []
    st.session_state.chat_sessions = []
    st.session_state.start_date = None
    st.session_state.end_date = None


def api_call(method, endpoint, token=None, **kwargs):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"{FASTAPI_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, **kwargs)
        elif method == "POST":
            response = requests.post(url, headers=headers, **kwargs)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, **kwargs)
        else:
            return {"error": f"Unsupported method: {method}"}

        if response.status_code == 401:
            st.session_state.authenticated = False
            st.query_params.clear()
            st.rerun()

        if response.status_code < 400:
            return response.json()

        try:
            return {"error": response.json().get("detail", "Error")}
        except Exception:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as exc:
        return {"error": str(exc)}


def get_chat_sessions_api(token):
    return api_call("GET", "/chat-sessions/", token)


def get_session_messages_api(token, session_id):
    result = api_call("GET", f"/chat-history/{session_id}", token)
    return result if isinstance(result, list) else []


def delete_chat_session_api(token, session_id):
    return api_call("DELETE", f"/chat-sessions/{session_id}", token)


# ────────────────────────────────────────────────
# Login / Register
# ────────────────────────────────────────────────
if not st.session_state.authenticated:
    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.markdown(
            """
            <div style="text-align:center; padding: 2rem 0 1.5rem 0;">
                <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                            background:linear-gradient(135deg,#60a5fa,#6366f1);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            background-clip:text;letter-spacing:-0.04em;">
                    ⬡ Velocis AI
                </div>
                <div style="color:#4a5878;font-size:0.82rem;margin-top:0.3rem;letter-spacing:0.04em;">
                    SECURE DOCUMENT INTELLIGENCE
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔒  Sign In", "📝  Create Account"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="your_username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Sign In", use_container_width=True, type="primary"):
                    result = api_call("POST", "/login", json={"username": username, "password": password})
                    if result.get("error"):
                        st.error(result["error"])
                    elif "access_token" in result:
                        st.session_state.authenticated = True
                        st.session_state.token = result["access_token"]
                        st.session_state.username = result["username"]
                        st.query_params.update({"token": result["access_token"], "user": result["username"]})
                        st.success("Welcome back!")
                        st.rerun()

        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="choose_a_username")
                new_email = st.text_input("Email", placeholder="you@company.com")
                new_password = st.text_input("Password", type="password", placeholder="min. 8 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        result = api_call(
                            "POST",
                            "/register",
                            json={"username": new_username, "email": new_email, "password": new_password},
                        )
                        if result.get("error"):
                            st.error(result["error"])
                        elif "access_token" in result:
                            st.session_state.authenticated = True
                            st.session_state.token = result["access_token"]
                            st.session_state.username = result["username"]
                            st.query_params.update({"token": result["access_token"], "user": result["username"]})
                            st.success("Account created successfully!")
                            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;color:#4a5878;font-size:0.7rem;margin-top:1rem;'>© 2026 Velocis Intelligence Unit</div>",
            unsafe_allow_html=True,
        )
    st.stop()


# ────────────────────────────────────────────────
# Main layout — Header
# ────────────────────────────────────────────────
col_brand, col_user, col_logout = st.columns([5, 1.5, 0.7])
with col_brand:
    st.markdown(
        '<span class="header-brand">⬡ Velocis AI</span>'
        '<span style="color:#4a5878;font-size:0.75rem;margin-left:0.75rem;letter-spacing:0.05em;">DOCUMENT INTELLIGENCE</span>',
        unsafe_allow_html=True,
    )
with col_user:
    st.markdown(
        f'<div style="text-align:right;padding-top:0.45rem;font-size:0.82rem;color:#8b9ab5;">'
        f'👤 <strong style="color:#f0f4ff">{st.session_state.username}</strong></div>',
        unsafe_allow_html=True,
    )
with col_logout:
    if st.button("Logout", type="primary", use_container_width=True):
        st.session_state.authenticated = False
        st.query_params.clear()
        st.rerun()

st.markdown("<hr style='margin:0.5rem 0 0.85rem 0;'>", unsafe_allow_html=True)

left_col, center_col, right_col = st.columns([1, 3, 1], gap="small")

# ────────────────────────────────────────────────
# LEFT: Documents + Filters
# ────────────────────────────────────────────────
with left_col:
    # Refresh docs from API if needed
    if not st.session_state.uploaded_docs:
        docs = api_call("GET", "/documents/", st.session_state.token)
        if isinstance(docs, list):
            st.session_state.uploaded_docs = docs

    st.markdown('<div class="section-title">📁 &nbsp;Documents</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        f"Upload (max {MAX_UPLOAD_FILES_PER_BATCH} files at once)",
        type=["pdf", "doc", "docx", "xlsx", "csv", "ppt", "pptx", "txt", "py", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help=f"Select up to {MAX_UPLOAD_FILES_PER_BATCH} files per upload. You can upload as many times as needed.",
    )

    if uploaded_files:
        # Enforce per-batch limit
        if len(uploaded_files) > MAX_UPLOAD_FILES_PER_BATCH:
            st.warning(
                f"⚠️ You selected {len(uploaded_files)} files, but only {MAX_UPLOAD_FILES_PER_BATCH} are allowed per upload. "
                f"The first {MAX_UPLOAD_FILES_PER_BATCH} will be uploaded."
            )
            uploaded_files = uploaded_files[:MAX_UPLOAD_FILES_PER_BATCH]

        if st.button("⬆ Upload Files", use_container_width=True, type="primary"):
            files_data = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
            result = api_call("POST", "/upload-documents/", st.session_state.token, files=files_data, timeout=300)
            if isinstance(result, list):
                st.success(f"✓ {len(result)} document(s) uploaded")
                st.session_state.uploaded_docs = []
                st.rerun()
            elif result.get("error"):
                st.error(result["error"])

    docs_panel = st.container(height=330, border=True, key="docs_panel")
    with docs_panel:
        if st.session_state.uploaded_docs:
            for doc in st.session_state.uploaded_docs:
                filename = doc["filename"]
                ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else "?"
                is_selected = str(doc["id"]) in st.session_state.selected_doc_ids
                display_name = filename if len(filename) <= 18 else filename[:16] + "…"

                col_chk, col_name, col_del = st.columns([0.3, 3.5, 0.6], vertical_alignment="center")

                with col_chk:
                    checked = st.checkbox(
                        filename,
                        value=is_selected,
                        key=f"doc_{doc['id']}",
                        help=filename,
                        label_visibility="collapsed",
                    )
                    if checked:
                        if str(doc["id"]) not in st.session_state.selected_doc_ids:
                            st.session_state.selected_doc_ids.append(str(doc["id"]))
                    else:
                        if str(doc["id"]) in st.session_state.selected_doc_ids:
                            st.session_state.selected_doc_ids.remove(str(doc["id"]))

                with col_name:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:0.4rem;padding:0.1rem 0;">'
                        f'<span style="font-size:0.78rem;color:#c8d6f0;white-space:nowrap;overflow:hidden;'
                        f'text-overflow:ellipsis;" title="{filename}">{display_name}</span>'
                        f'<span class="file-type-badge">{ext}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                with col_del:
                    if st.button("✕", key=f"del_{doc['id']}", help=f"Delete {filename}", use_container_width=True):
                        api_call("DELETE", f"/documents/{doc['id']}", st.session_state.token)
                        st.session_state.uploaded_docs = []
                        st.rerun()
        else:
            st.markdown(
                '<div style="text-align:center;padding:2rem 0.5rem;color:#4a5878;font-size:0.8rem;">'
                '📭<br>No documents yet.<br>Upload files to get started.</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title" style="margin-top:1rem;">🔍 &nbsp;Filters</div>', unsafe_allow_html=True)
    use_date = st.checkbox("Enable date filter", value=False)
    if use_date:
        start_date = st.date_input("From", value=date(2023, 1, 1))
        end_date = st.date_input("To", value=date.today())
        if start_date <= end_date:
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
        else:
            st.warning("Start date must be before end date.")
            st.session_state.start_date = None
            st.session_state.end_date = None
    else:
        st.session_state.start_date = None
        st.session_state.end_date = None


# ────────────────────────────────────────────────
# CENTER: Chat area
# ────────────────────────────────────────────────
with center_col:
    chat_header_l, chat_header_r = st.columns([4, 1], vertical_alignment="center")
    with chat_header_l:
        selected_count = len(st.session_state.selected_doc_ids)
        context_hint = (
            f'<span style="font-size:0.75rem;color:#3b82f6;margin-left:0.6rem;">'
            f'({selected_count} doc{"s" if selected_count != 1 else ""} in context)</span>'
            if selected_count > 0
            else '<span style="font-size:0.75rem;color:#4a5878;margin-left:0.6rem;">(all docs)</span>'
        )
        st.markdown(
            f'<div style="padding:0.3rem 0;">'
            f'<span style="font-family:Syne,sans-serif;font-size:1.05rem;font-weight:700;">💬 Chat</span>'
            f'{context_hint}</div>',
            unsafe_allow_html=True,
        )
    with chat_header_r:
        if st.button("✨ New Chat", use_container_width=True):
            st.session_state.current_session_id = str(uuid.uuid4())
            st.session_state.chat_messages = []
            st.rerun()

    chat_placeholder = st.container(height=430, border=False)
    with chat_placeholder:
        if not st.session_state.chat_messages:
            st.markdown(
                """
                <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                            height:300px;text-align:center;color:#4a5878;">
                    <div style="font-size:2.5rem;margin-bottom:0.75rem;opacity:0.4;">⬡</div>
                    <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:600;color:#2a3f5f;">
                        Start a conversation
                    </div>
                    <div style="font-size:0.8rem;margin-top:0.4rem;max-width:280px;line-height:1.6;">
                        Upload documents and ask anything — summaries, comparisons, specific data points.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("Ask about your documents…"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with chat_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    payload = {
                        "query": prompt,
                        "session_id": st.session_state.current_session_id,
                        "document_ids": st.session_state.selected_doc_ids if st.session_state.selected_doc_ids else None,
                        "start_date": st.session_state.start_date.isoformat() if st.session_state.start_date else None,
                        "end_date": st.session_state.end_date.isoformat() if st.session_state.end_date else None,
                    }
                    response = api_call("POST", "/chat/", st.session_state.token, json=payload)

                if response.get("error"):
                    st.error(response["error"])
                elif "answer" in response:
                    answer = response["answer"]
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                    st.markdown(answer, unsafe_allow_html=True)
                else:
                    st.warning("No valid response received from server.")

        st.rerun()


# ────────────────────────────────────────────────
# RIGHT: Chat History
# ────────────────────────────────────────────────
with right_col:
    hist_col1, hist_col2 = st.columns([3, 1], vertical_alignment="center")
    with hist_col1:
        st.markdown(
            '<div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;padding:0.3rem 0;">📜 History</div>',
            unsafe_allow_html=True,
        )
    with hist_col2:
        if st.button("↻", use_container_width=True, help="Refresh history"):
            st.session_state.chat_sessions = []
            st.rerun()

    if not st.session_state.chat_sessions:
        sessions = get_chat_sessions_api(st.session_state.token)
        if isinstance(sessions, list):
            st.session_state.chat_sessions = sessions

    history_panel = st.container(height=490, border=True, key="history_panel")
    with history_panel:
        if st.session_state.chat_sessions:
            today = datetime.now().date()
            sessions_by_date = {}

            for session in st.session_state.chat_sessions:
                try:
                    last_msg = datetime.fromisoformat(session["last_message"].replace("Z", "+00:00"))
                    date_key = last_msg.date()

                    if date_key == today:
                        display = "Today"
                    elif (today - date_key).days == 1:
                        display = "Yesterday"
                    else:
                        display = date_key.strftime("%d %b %Y")

                    sessions_by_date.setdefault(display, []).append(session)
                except Exception:
                    sessions_by_date.setdefault("Other", []).append(session)

            for display_date in sorted(
                sessions_by_date.keys(),
                key=lambda x: (x not in ["Today", "Yesterday"], x),
                reverse=True,
            ):
                st.markdown(
                    f'<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;'
                    f'text-transform:uppercase;color:#4a5878;padding:0.4rem 0 0.25rem 0;">'
                    f'{display_date}</div>',
                    unsafe_allow_html=True,
                )
                for session in sessions_by_date[display_date]:
                    sess_col1, sess_col2 = st.columns([3, 1], vertical_alignment="center")
                    with sess_col1:
                        if st.button(
                            "💬 Chat",
                            key=f"sess_{session['session_id']}",
                            use_container_width=True,
                            help=f"Session {session['session_id'][:8]}…",
                        ):
                            st.session_state.current_session_id = session["session_id"]
                            messages = get_session_messages_api(st.session_state.token, session["session_id"])
                            st.session_state.chat_messages = [
                                {"role": m["role"], "content": m["content"]} for m in messages
                            ]
                            st.rerun()
                    with sess_col2:
                        if st.button("✕", key=f"del_sess_{session['session_id']}", help="Delete session", use_container_width=True):
                            delete_chat_session_api(st.session_state.token, session["session_id"])
                            st.session_state.chat_sessions = []
                            st.rerun()
        else:
            st.markdown(
                '<div style="text-align:center;padding:2rem 0.5rem;color:#4a5878;font-size:0.8rem;">'
                '🗂<br>No previous chats yet.</div>',
                unsafe_allow_html=True,
            )

st.markdown("<hr style='margin:0.75rem 0 0.4rem 0;'>", unsafe_allow_html=True)
st.caption("© 2026 Velocis Intelligence Unit  •  Secure Document Analysis  •  All rights reserved")
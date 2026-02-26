import uuid
from datetime import date, datetime

import requests
import streamlit as st

FASTAPI_URL = "http://localhost:8000"
MAX_UPLOAD_FILES_PER_BATCH = 30

st.set_page_config(page_title="Velocis AI Assistant", layout="wide", page_icon="🤖")

# ── Light theme colour palette ────────────────────────────────────────────────
LIGHT = {
    "bg":          "#f0f4fb",
    "bg2":         "#e4e9f5",
    "card":        "#ffffff",
    "card_hover":  "#eef2ff",
    "border":      "#c8d4e8",
    "border2":     "#9aaac4",
    "accent":      "#2563eb",
    "accent_glow": "rgba(37,99,235,0.15)",
    "accent_sub":  "rgba(37,99,235,0.09)",
    "text":        "#0f172a",
    "text2":       "#334155",
    "muted":       "#64748b",
    "filename":    "#1e293b",
    "danger":      "#dc2626",
    "danger_sub":  "rgba(220,38,38,0.08)",
    "scroll":      "#9aaac4",
    "hr":          "#c8d4e8",
    "shadow":      "rgba(15,23,42,0.08)",
    "up_bg":       "#f8faff",
    "up_border":   "#9aaac4",
    "up_text":     "#334155",
    "up_btn":      "#e2e8f0",
    "up_btn_fg":   "#0f172a",
    "inp_bg":      "#ffffff",
}
T = LIGHT

# ── Inject light theme CSS (with checkbox tick fix and green upload button) ───
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & base ── */
*, *::before, *::after {{
    font-family: 'DM Sans', sans-serif !important;
    box-sizing: border-box;
}}

/* ── Full app background & text ── */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stBottom"],
section.main,
.main .block-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {T['bg']} !important;
    color: {T['text']} !important;
}}

[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stHeader"]  {{ height: 0 !important; display: none !important; }}
.block-container          {{ padding-top: 1.4rem !important; max-width: 100% !important; }}

/* ── Typography ── */
h1, h2, h3 {{
    font-family: 'Syne', sans-serif !important;
    color: {T['text']} !important;
    letter-spacing: -0.02em;
}}

/* ── All plain text nodes ── */
p, span, label, li, td, th {{
    color: {T['text']};
}}

/* ───────────────────────────────────────
   FILE UPLOADER
─────────────────────────────────────── */
[data-testid="stFileUploader"],
[data-testid="stFileUploaderDropzone"] {{
    background: {T['up_bg']} !important;
    border: 1.5px dashed {T['up_border']} !important;
    border-radius: 10px !important;
}}
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] > div {{
    background: {T['up_bg']} !important;
    border-radius: 10px !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] *,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span {{
    color: {T['up_text']} !important;
}}
[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] button {{
    background: {T['up_btn']} !important;
    color: {T['up_btn_fg']} !important;
    border: 1.5px solid {T['border2']} !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: border-color 0.15s, color 0.15s !important;
}}
[data-testid="stFileUploader"] button:hover,
[data-testid="stFileUploaderDropzone"] button:hover {{
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
}}
[data-testid="stFileUploaderFile"],
[data-testid="uploadedFileData"],
[data-testid="stFileUploaderFileName"] {{
    background: {T['card']} !important;
    color: {T['text']} !important;
}}
[data-testid="stFileUploaderDeleteBtn"] button {{
    background: transparent !important;
    border: none !important;
    color: {T['muted']} !important;
}}
[data-testid="stFileUploaderDeleteBtn"] button:hover {{
    color: {T['danger']} !important;
}}

/* ───────────────────────────────────────
   PANELS
─────────────────────────────────────── */
.st-key-docs_panel,
.st-key-history_panel {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 12px !important;
}}

/* ── Force all inner elements of docs panel to be transparent by default,
      then restore backgrounds for checkboxes and buttons. ── */
.st-key-docs_panel * {{
    background: transparent !important;
}}
.st-key-docs_panel [data-testid="stCheckbox"] > div:first-child {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 4px;
}}
/* Ensure checkbox tick is visible (white on accent) */
.st-key-docs_panel [data-testid="stCheckbox"] svg {{
    color: {T['accent']} !important;
    fill: {T['accent']} !important;
}}
/* 3. THE FIX: TARGET THE INNER BOX SPECIFICALLY */
/* This selector is more specific than the '*' selector above */
.st-key-docs_panel [data-testid="stCheckbox"] input:checked ~ div {{
    background-color: red !important;
}}
.st-key-docs_panel [data-testid="stCheckbox"] input:checked + div svg {{
    color: white !important;
    fill: white !important;
}}
.st-key-docs_panel button[class*="del_"] {{
    background: transparent !important;
}}
.st-key-docs_panel button[class*="del_"]:hover {{
    background: {T['danger_sub']} !important;
}}

/* ── Header brand ── */
.header-brand {{
    font-family: 'Syne', sans-serif !important;
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
}}
.header-sublabel {{
    font-size: 0.75rem;
    margin-left: 0.75rem;
    letter-spacing: 0.05em;
    color: {T['muted']} !important;
}}
.username-display {{
    text-align: right;
    padding-top: 0.45rem;
    font-size: 0.82rem;
    color: {T['text2']} !important;
}}
.username-display strong {{ color: {T['text']} !important; }}

/* ── Section headings ── */
.section-title {{
    font-family: 'Syne', sans-serif !important;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {T['muted']} !important;
    padding: 0 0 0.5rem 0;
    border-bottom: 1px solid {T['border']};
    margin-bottom: 0.75rem;
}}

/* ── File type badge ── */
.file-type-badge {{
    display: inline-block;
    font-size: 0.55rem !important;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 1px 5px;
    border-radius: 4px;
    background: {T['accent_sub']} !important;
    color: {T['accent']} !important;
    border: 1px solid rgba(59,130,246,0.28);
    vertical-align: middle;
}}
.doc-name-span {{
    font-size: 0.78rem;
    color: {T['filename']} !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.empty-state-text {{
    text-align: center;
    padding: 2rem 0.5rem;
    font-size: 0.8rem;
    color: {T['muted']} !important;
}}
.hist-date-label {{
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {T['muted']} !important;
    padding: 0.4rem 0 0.25rem 0;
}}
.ctx-all {{ font-size:0.75rem; color:{T['muted']} !important; margin-left:0.6rem; }}
.ctx-sel {{ font-size:0.75rem; color:{T['accent']} !important; margin-left:0.6rem; }}

/* ───────────────────────────────────────
   BUTTONS
─────────────────────────────────────── */
/* Primary (Logout, Sign In) – keep blue */
[data-testid="stBaseButton-primary"] button,
[data-testid="stBaseButton-primary"] button:focus {{
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    transition: opacity 0.2s, transform 0.15s !important;
}}
[data-testid="stBaseButton-primary"] button:hover {{
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}}

/* Upload button – green gradient (targeted by key) */
button[data-testid="baseButton-primary"][key="upload_files_btn"] {{
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
}}

/* Secondary */
[data-testid="stBaseButton-secondary"] button,
[data-testid="stBaseButton-secondary"] button:focus {{
    background: {T['card']} !important;
    border: 1.5px solid {T['border2']} !important;
    border-radius: 8px !important;
    color: {T['text2']} !important;
    font-weight: 500 !important;
    transition: background 0.18s, border-color 0.18s, color 0.18s !important;
}}
[data-testid="stBaseButton-secondary"] button:hover {{
    background: {T['card_hover']} !important;
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
}}

/* Delete ghost buttons */
[class*="del_"] button,
[data-testid*="del_"] button {{
    background: transparent !important;
    border: 1px solid transparent !important;
    color: {T['muted']} !important;
    border-radius: 6px !important;
    padding: 0.15rem 0.35rem !important;
    font-size: 0.75rem !important;
    min-height: unset !important;
    height: 1.6rem !important;
    transition: background 0.15s, border-color 0.15s, color 0.15s !important;
}}
[class*="del_"] button:hover,
[data-testid*="del_"] button:hover {{
    background: {T['danger_sub']} !important;
    border-color: rgba(220,38,38,0.35) !important;
    color: {T['danger']} !important;
}}

/* ───────────────────────────────────────
   INPUTS
─────────────────────────────────────── */
input[type="text"],
input[type="password"] {{
    background: {T['inp_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
input[type="text"]:focus,
input[type="password"]:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent_glow']} !important;
    outline: none !important;
}}
[data-testid="stTextInput"] label,
[data-testid="stDateInput"]  label {{
    color: {T['text2']} !important;
    font-size: 0.82rem !important;
}}
[data-testid="stDateInput"] input {{
    background: {T['inp_bg']} !important;
    color: {T['text']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
}}

/* ── Chat input ── */
[data-testid="stChatInput"] > div {{
    background: {T['card']} !important;
    border: 1.5px solid {T['border2']} !important;
    border-radius: 12px !important;
}}
[data-testid="stChatInput"] > div:focus-within {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent_glow']} !important;
}}
[data-testid="stChatInput"] textarea {{
    background: {T['card']} !important;
    color: {T['text']} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {T['muted']} !important;
}}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    border: none !important;
    padding: 0.25rem 0 !important;
}}

/* ── Checkboxes (global) ── */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] span {{ color: {T['text2']} !important; font-size: 0.8rem !important; }}
[data-testid="stCheckbox"] > div:first-child {{
    background: {T['card']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 4px;
}}
[data-testid="stCheckbox"] svg {{
    color: {T['accent']} !important;
    fill: {T['accent']} !important;
}}
[data-testid="stCheckbox"] input:checked + div svg {{
    color: white !important;
    fill: white !important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] button {{
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: {T['text2']} !important;
    background: transparent !important;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{ color: {T['accent']} !important; }}
[data-testid="stTabs"] > div:first-child {{ background: {T['bg2']} !important; border-radius: 8px 8px 0 0; }}

/* ── Divider ── */
hr {{ border-color: {T['hr']} !important; margin: 0.6rem 0 !important; }}

/* ── Alerts ── */
[data-testid="stAlert"] {{ border-radius: 8px !important; font-size: 0.82rem !important; }}

/* ── Login card ── */
.login-card {{
    background: {T['card']};
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 2rem 2.25rem;
    box-shadow: 0 4px 24px {T['shadow']};
}}

/* ── Caption ── */
[data-testid="stCaptionContainer"] {{ color: {T['muted']} !important; font-size: 0.72rem !important; text-align: center; }}

/* ── Scrollbars ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['scroll']}; border-radius: 99px; }}
::-webkit-scrollbar-thumb:hover {{ background: {T['accent']}; }}

/* ── Markdown containers inherit theme ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {{
    color: {T['text']} !important;
}}

/* ── Disable chat input during upload ── */
.chat-disabled {{
    opacity: 0.5;
    pointer-events: none;
}}
</style>
""", unsafe_allow_html=True)

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
    st.session_state.upload_key = 0  # for resetting file uploader
    st.session_state.upload_in_progress = False  # to disable chat


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
            f"""<div style="text-align:center;padding:1.5rem 0 1.2rem 0;">
                <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                            background:linear-gradient(135deg,#3b82f6,#6366f1);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            background-clip:text;letter-spacing:-0.04em;">⬡ Doc Analyzer</div>
                <div style="font-size:0.82rem;margin-top:0.3rem;letter-spacing:0.04em;color:{T['muted']};">
                    SECURE DOCUMENT INTELLIGENCE
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # st.markdown('<div class="login-card">', unsafe_allow_html=True)
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
                        result = api_call("POST", "/register",
                            json={"username": new_username, "email": new_email, "password": new_password})
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
            f"<div style='text-align:center;font-size:0.7rem;margin-top:1rem;color:{T['muted']};'>"
            "© 2026 Velocis Intelligence Unit</div>",
            unsafe_allow_html=True,
        )
    st.stop()


# ────────────────────────────────────────────────
# Main layout — Header
# ────────────────────────────────────────────────
col_brand, col_user, col_logout = st.columns([5, 2, 1], vertical_alignment="center")
with col_brand:
    st.markdown(
        '<span class="header-brand">⬡ Doc Analyzer</span>'
        '<span class="header-sublabel">DOCUMENT INTELLIGENCE</span>',
        unsafe_allow_html=True,
    )
with col_user:
    st.markdown(
        f'<div class="username-display">👤 <strong>{st.session_state.username}</strong></div>',
        unsafe_allow_html=True,
    )
with col_logout:
    if st.button("Logout", type="primary", use_container_width=True):
        st.session_state.authenticated = False
        st.query_params.clear()
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

left_col, center_col, right_col = st.columns([1, 3, 1], gap="small")

# ────────────────────────────────────────────────
# LEFT: Documents + (Filters commented out)
# ────────────────────────────────────────────────
with left_col:
    if not st.session_state.uploaded_docs:
        docs = api_call("GET", "/documents/", st.session_state.token)
        if isinstance(docs, list):
            st.session_state.uploaded_docs = docs

    st.markdown('<div class="section-title">📁 &nbsp;Documents</div>', unsafe_allow_html=True)

    # Use a dynamic key to reset the uploader after successful upload
    uploaded_files = st.file_uploader(
        f"Upload (max {MAX_UPLOAD_FILES_PER_BATCH} files at once)",
        type=["pdf", "doc", "docx", "xlsx", "csv", "ppt", "pptx", "txt", "py", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help=f"Select up to {MAX_UPLOAD_FILES_PER_BATCH} files per upload.",
        key=f"file_uploader_{st.session_state.upload_key}",
    )

    if uploaded_files and not st.session_state.upload_in_progress:
        if len(uploaded_files) > MAX_UPLOAD_FILES_PER_BATCH:
            st.warning(
                f"⚠️ You selected {len(uploaded_files)} files, but only "
                f"{MAX_UPLOAD_FILES_PER_BATCH} are allowed per upload. "
                f"The first {MAX_UPLOAD_FILES_PER_BATCH} will be uploaded."
            )
            uploaded_files = uploaded_files[:MAX_UPLOAD_FILES_PER_BATCH]

        # Upload button with green color (targeted by key)
        if st.button("⬆ Upload Files", use_container_width=True, type="primary", key="upload_files_btn"):
            # Disable chat during upload
            st.session_state.upload_in_progress = True
            progress_bar = st.progress(0, text="Uploading files...")
            total_files = len(uploaded_files)
            success_count = 0

            for i, f in enumerate(uploaded_files):
                # Send one file at a time
                files_data = [("files", (f.name, f.getvalue(), f.type))]
                result = api_call("POST", "/upload-documents/", st.session_state.token,
                                  files=files_data, timeout=300)
                if isinstance(result, list) and len(result) > 0:
                    success_count += 1
                elif result.get("error"):
                    st.error(f"Failed to upload {f.name}: {result['error']}")
                # Update progress
                progress_bar.progress((i + 1) / total_files, text=f"Uploaded {i+1} of {total_files} files")

            progress_bar.empty()
            if success_count > 0:
                st.success(f"✓ {success_count} document(s) uploaded")
                # Refresh document list
                st.session_state.uploaded_docs = []
                # Reset uploader by incrementing key
                st.session_state.upload_key += 1
            # Re-enable chat
            st.session_state.upload_in_progress = False
            st.rerun()

    docs_panel = st.container(height=368, border=True, key="docs_panel")
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
                        filename, value=is_selected,
                        key=f"doc_{doc['id']}", help=filename,
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
                        f'<span class="doc-name-span" title="{filename}">{display_name}</span>'
                        f'<span class="file-type-badge">{ext}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with col_del:
                    if st.button("✕", key=f"del_{doc['id']}",
                                 help=f"Delete {filename}", use_container_width=True):
                        api_call("DELETE", f"/documents/{doc['id']}", st.session_state.token)
                        st.session_state.uploaded_docs = []
                        st.rerun()
        else:
            st.markdown(
                '<div class="empty-state-text">📭<br>No documents yet.<br>Upload files to get started.</div>',
                unsafe_allow_html=True,
            )

    # ── Filters (commented out) ──
    # ...


# ────────────────────────────────────────────────
# CENTER: Chat (disable during upload)
# ────────────────────────────────────────────────
with center_col:
    chat_header_l, chat_header_r = st.columns([4, 1], vertical_alignment="center")
    with chat_header_l:
        selected_count = len(st.session_state.selected_doc_ids)
        ctx_html = (
            f'<span class="ctx-sel">({selected_count} doc{"s" if selected_count != 1 else ""} in context)</span>'
            if selected_count > 0
            else '<span class="ctx-all">(all docs)</span>'
        )
        st.markdown(
            f'<div style="padding:0.3rem 0;">'
            f'<span style="font-family:Syne,sans-serif;font-size:1.05rem;font-weight:700;color:{T["text"]};">'
            f'💬 Chat</span>{ctx_html}</div>',
            unsafe_allow_html=True,
        )
    with chat_header_r:
        # Disable "New Chat" button during upload
        if st.button("✨ New Chat", use_container_width=True, disabled=st.session_state.upload_in_progress):
            st.session_state.current_session_id = str(uuid.uuid4())
            st.session_state.chat_messages = []
            st.rerun()

    # Apply a CSS class to the chat container if upload in progress
    chat_container_class = "chat-disabled" if st.session_state.upload_in_progress else ""
    chat_placeholder = st.container(height=429, border=False)
    with chat_placeholder:
        if not st.session_state.chat_messages:
            st.markdown(
                f"""<div style="display:flex;flex-direction:column;align-items:center;
                            justify-content:center;height:300px;text-align:center;">
                    <div style="font-size:2.5rem;margin-bottom:0.75rem;opacity:0.2;">⬡</div>
                    <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:600;color:{T['text2']};">
                        Start a conversation
                    </div>
                    <div style="font-size:0.8rem;margin-top:0.4rem;max-width:280px;line-height:1.6;color:{T['muted']};">
                        Upload documents and ask anything — you can set target document by selecting them in the left panel.
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
        for msg in st.session_state.chat_messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"], unsafe_allow_html=True)

    # Chat input disabled during upload
    prompt = st.chat_input("Ask about your documents…", disabled=st.session_state.upload_in_progress)
    if prompt and not st.session_state.upload_in_progress:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with chat_placeholder:
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar="🤖"):
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
            f'<div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;'
            f'padding:0.3rem 0;color:{T["text"]};">📜 History</div>',
            unsafe_allow_html=True,
        )
    with hist_col2:
        if st.button("↻", use_container_width=True, help="Refresh history", disabled=st.session_state.upload_in_progress):
            st.session_state.chat_sessions = []
            st.rerun()

    if not st.session_state.chat_sessions:
        sessions = get_chat_sessions_api(st.session_state.token)
        if isinstance(sessions, list):
            st.session_state.chat_sessions = sessions

    history_panel = st.container(height=498, border=True, key="history_panel")
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
                st.markdown(f'<div class="hist-date-label">{display_date}</div>', unsafe_allow_html=True)
                for session in sessions_by_date[display_date]:
                    sess_col1, sess_col2 = st.columns([3, 1], vertical_alignment="center")
                    with sess_col1:
                        if st.button("💬 Chat", key=f"sess_{session['session_id']}",
                                     use_container_width=True,
                                     help=f"Session {session['session_id'][:8]}…",
                                     disabled=st.session_state.upload_in_progress):
                            st.session_state.current_session_id = session["session_id"]
                            messages = get_session_messages_api(
                                st.session_state.token, session["session_id"])
                            st.session_state.chat_messages = [
                                {"role": m["role"], "content": m["content"]} for m in messages]
                            st.rerun()
                    with sess_col2:
                        if st.button("✕", key=f"del_sess_{session['session_id']}",
                                     help="Delete session", use_container_width=True,
                                     disabled=st.session_state.upload_in_progress):
                            delete_chat_session_api(st.session_state.token, session["session_id"])
                            st.session_state.chat_sessions = []
                            st.rerun()
        else:
            st.markdown(
                '<div class="empty-state-text">🗂<br>No previous chats yet.</div>',
                unsafe_allow_html=True,
            )

st.markdown("<hr>", unsafe_allow_html=True)
st.caption("© 2026 Velocis Intelligence Unit  •  Secure Document Analysis  •  All rights reserved")
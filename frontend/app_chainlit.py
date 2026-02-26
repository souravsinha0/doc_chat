"""
Velocis AI — Chainlit Frontend
Run with: chainlit run app.py -w
"""

import uuid
from datetime import datetime
from typing import Optional

import requests
import chainlit as cl

# ────────────────────────────────────────────────
# Configurable Constants
# ────────────────────────────────────────────────
FASTAPI_URL = "http://localhost:8000"
MAX_UPLOAD_FILES_PER_BATCH = 30  # Max files per single upload batch (configurable)
ALLOWED_EXTENSIONS = ["pdf", "doc", "docx", "xlsx", "csv", "ppt", "pptx", "txt", "py", "md"]


# ────────────────────────────────────────────────
# API Helpers
# ────────────────────────────────────────────────
def api_call(method: str, endpoint: str, token: Optional[str] = None, **kwargs):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"{FASTAPI_URL}{endpoint}"
    try:
        response = getattr(requests, method.lower())(url, headers=headers, **kwargs)
        if response.status_code < 400:
            return response.json()
        try:
            return {"error": response.json().get("detail", f"HTTP {response.status_code}")}
        except Exception:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as exc:
        return {"error": str(exc)}


def get_documents(token: str):
    result = api_call("GET", "/documents/", token)
    return result if isinstance(result, list) else []


def delete_document(token: str, doc_id: str):
    return api_call("DELETE", f"/documents/{doc_id}", token)


def get_chat_sessions(token: str):
    result = api_call("GET", "/chat-sessions/", token)
    return result if isinstance(result, list) else []


def get_session_messages(token: str, session_id: str):
    result = api_call("GET", f"/chat-history/{session_id}", token)
    return result if isinstance(result, list) else []


def delete_chat_session(token: str, session_id: str):
    return api_call("DELETE", f"/chat-sessions/{session_id}", token)


def upload_documents(token: str, files: list):
    files_data = [("files", (f["name"], f["content"], f["mime"])) for f in files]
    return api_call("POST", "/upload-documents/", token, files=files_data, timeout=600)


def send_chat(token: str, query: str, session_id: str, doc_ids: list,
              start_date=None, end_date=None):
    payload = {
        "query": query,
        "session_id": session_id,
        "document_ids": doc_ids if doc_ids else None,
        "start_date": start_date,
        "end_date": end_date,
    }
    return api_call("POST", "/chat/", token, json=payload)


# ────────────────────────────────────────────────
# Chat Start — show login prompt
# ────────────────────────────────────────────────
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("token", None)
    cl.user_session.set("username", None)
    cl.user_session.set("session_id", str(uuid.uuid4()))
    cl.user_session.set("selected_doc_ids", [])
    cl.user_session.set("documents", [])
    cl.user_session.set("start_date", None)
    cl.user_session.set("end_date", None)
    cl.user_session.set("auth_step", "choose")
    cl.user_session.set("_session_map", {})

    await cl.Message(
        content=(
            "## ⬡ Velocis Document Intelligence\n\n"
            "**Secure AI-powered document analysis.**\n\n"
            "Type **`login`** to sign in, or **`register`** to create a new account."
        )
    ).send()


# ────────────────────────────────────────────────
# Main message router
# ────────────────────────────────────────────────
@cl.on_message
async def on_message(message: cl.Message):
    token = cl.user_session.get("token")
    auth_step = cl.user_session.get("auth_step", "choose")

    # ── Not authenticated yet ──
    if not token:
        await _handle_auth(message, auth_step)
        return

    text = message.content.strip()

    # ── File upload attached ──
    if message.elements:
        await _handle_upload(message)
        # If there's also text, process it as a chat query after upload
        if text:
            await _handle_chat(text)
        return

    # ── Slash commands ──
    cmd = text.lower().split()[0] if text else ""

    if cmd == "/docs":
        await _show_documents()
    elif cmd == "/history":
        await _show_history()
    elif cmd == "/newchat":
        cl.user_session.set("session_id", str(uuid.uuid4()))
        await cl.Message(content="✨ **New chat session started.** Previous context cleared.").send()
    elif cmd == "/select":
        await _handle_select(text)
    elif cmd == "/deselect":
        await _handle_deselect(text)
    elif cmd == "/delete":
        await _handle_delete_doc(text)
    elif cmd == "/load":
        await _handle_load_session(text)
    elif cmd == "/deletesession":
        await _handle_delete_session(text)
    elif cmd == "/datefilter":
        await _handle_date_filter(text)
    elif cmd == "/clearfilter":
        cl.user_session.set("start_date", None)
        cl.user_session.set("end_date", None)
        await cl.Message(content="🗓 Date filter cleared.").send()
    elif cmd == "/logout":
        await _handle_logout()
    elif cmd == "/help":
        await _show_help()
    elif text.startswith("/"):
        await cl.Message(
            content=f"⚠️ Unknown command `{cmd}`. Type `/help` to see all available commands."
        ).send()
    else:
        # Regular chat query
        await _handle_chat(text)


# ────────────────────────────────────────────────
# Auth flow (step-by-step conversation)
# ────────────────────────────────────────────────
async def _handle_auth(message: cl.Message, step: str):
    text = message.content.strip()

    if step == "choose":
        if text.lower() == "login":
            cl.user_session.set("auth_step", "login_username")
            await cl.Message(content="🔒 **Sign In**\n\nEnter your **username**:").send()
        elif text.lower() == "register":
            cl.user_session.set("auth_step", "reg_username")
            await cl.Message(content="📝 **Create Account**\n\nChoose a **username**:").send()
        else:
            await cl.Message(
                content="Type **`login`** to sign in or **`register`** to create an account."
            ).send()

    # ── Login steps ──────────────────────────
    elif step == "login_username":
        cl.user_session.set("_tmp_username", text)
        cl.user_session.set("auth_step", "login_password")
        await cl.Message(content="🔑 Enter your **password**:").send()

    elif step == "login_password":
        username = cl.user_session.get("_tmp_username")
        result = api_call("POST", "/login", json={"username": username, "password": text})
        if result.get("error"):
            await cl.Message(
                content=f"❌ {result['error']}\n\nEnter your **username** again:"
            ).send()
            cl.user_session.set("auth_step", "login_username")
        elif "access_token" in result:
            await _complete_login(result["access_token"], result["username"])

    # ── Register steps ───────────────────────
    elif step == "reg_username":
        cl.user_session.set("_tmp_username", text)
        cl.user_session.set("auth_step", "reg_email")
        await cl.Message(content="📧 Enter your **email address**:").send()

    elif step == "reg_email":
        cl.user_session.set("_tmp_email", text)
        cl.user_session.set("auth_step", "reg_password")
        await cl.Message(content="🔑 Choose a **password**:").send()

    elif step == "reg_password":
        cl.user_session.set("_tmp_password", text)
        cl.user_session.set("auth_step", "reg_confirm")
        await cl.Message(content="🔑 **Confirm** your password:").send()

    elif step == "reg_confirm":
        password = cl.user_session.get("_tmp_password")
        if text != password:
            await cl.Message(
                content="❌ Passwords do not match.\n\nChoose a **password** again:"
            ).send()
            cl.user_session.set("auth_step", "reg_password")
        else:
            username = cl.user_session.get("_tmp_username")
            email = cl.user_session.get("_tmp_email")
            result = api_call(
                "POST", "/register",
                json={"username": username, "email": email, "password": password},
            )
            if result.get("error"):
                await cl.Message(
                    content=f"❌ {result['error']}\n\nType **`login`** or **`register`** to try again."
                ).send()
                cl.user_session.set("auth_step", "choose")
            elif "access_token" in result:
                await _complete_login(result["access_token"], result["username"])


async def _complete_login(token: str, username: str):
    cl.user_session.set("token", token)
    cl.user_session.set("username", username)
    cl.user_session.set("auth_step", "done")

    docs = get_documents(token)
    cl.user_session.set("documents", docs)

    await cl.Message(
        content=(
            f"## ✅ Welcome, **{username}**!\n\n"
            f"You're signed in to **Velocis Document Intelligence**.\n\n"
            f"| Quick actions | |\n"
            f"|---|---|\n"
            f"| 📎 Upload files | Attach files to any message |\n"
            f"| 💬 Chat | Type your question directly |\n"
            f"| 📁 Documents | `/docs` |\n"
            f"| 📜 History | `/history` |\n"
            f"| ❓ Help | `/help` |\n\n"
            f"_{len(docs)} document(s) in your library._"
        )
    ).send()


# ────────────────────────────────────────────────
# Document upload
# ────────────────────────────────────────────────
async def _handle_upload(message: cl.Message):
    token = cl.user_session.get("token")
    elements = [e for e in message.elements if hasattr(e, "name")]

    # Filter allowed extensions
    allowed, skipped = [], []
    for el in elements:
        ext = el.name.rsplit(".", 1)[-1].lower() if "." in el.name else ""
        if ext in ALLOWED_EXTENSIONS:
            allowed.append(el)
        else:
            skipped.append(el.name)

    if not allowed:
        await cl.Message(
            content=(
                f"⚠️ No supported files found.\n"
                f"Supported formats: `{', '.join(ALLOWED_EXTENSIONS)}`"
            )
        ).send()
        return

    # Enforce batch limit
    if len(allowed) > MAX_UPLOAD_FILES_PER_BATCH:
        over = [e.name for e in allowed[MAX_UPLOAD_FILES_PER_BATCH:]]
        allowed = allowed[:MAX_UPLOAD_FILES_PER_BATCH]
        await cl.Message(
            content=(
                f"⚠️ Batch limit is **{MAX_UPLOAD_FILES_PER_BATCH} files**. "
                f"Only the first {MAX_UPLOAD_FILES_PER_BATCH} will be uploaded.\n"
                f"Skipped (over limit): `{'`, `'.join(over)}`"
            )
        ).send()

    async with cl.Step(name=f"Uploading {len(allowed)} file(s)…", show_input=False) as step:
        files_data = []
        for el in allowed:
            try:
                if hasattr(el, "path") and el.path:
                    with open(el.path, "rb") as f:
                        content = f.read()
                elif hasattr(el, "content") and el.content:
                    content = el.content
                else:
                    skipped.append(el.name)
                    continue
                mime = getattr(el, "mime", "application/octet-stream") or "application/octet-stream"
                files_data.append({"name": el.name, "content": content, "mime": mime})
            except Exception as e:
                skipped.append(f"{el.name} (read error: {e})")

        if not files_data:
            step.output = "No readable files."
            await cl.Message(content="❌ Could not read any of the attached files.").send()
            return

        result = upload_documents(token, files_data)
        step.output = f"Processed {len(files_data)} file(s)."

    # Refresh doc list
    docs = get_documents(token)
    cl.user_session.set("documents", docs)

    if isinstance(result, list):
        names = [r.get("filename", "?") for r in result]
        msg = f"✅ **{len(result)} file(s) uploaded successfully:**\n"
        msg += "\n".join(f"  • `{n}`" for n in names)
        if skipped:
            msg += f"\n\n⚠️ Skipped: `{'`, `'.join(skipped)}`"
        msg += f"\n\n_Library now has **{len(docs)}** document(s). Use `/docs` to manage them._"
        await cl.Message(content=msg).send()
    else:
        await cl.Message(
            content=f"❌ Upload failed: {result.get('error', 'Unknown error')}"
        ).send()


# ────────────────────────────────────────────────
# Document listing & management
# ────────────────────────────────────────────────
async def _show_documents():
    token = cl.user_session.get("token")
    docs = get_documents(token)
    cl.user_session.set("documents", docs)
    selected_ids = cl.user_session.get("selected_doc_ids", [])

    if not docs:
        await cl.Message(
            content=(
                "📭 **No documents uploaded yet.**\n\n"
                "Attach files to any message to upload them."
            )
        ).send()
        return

    lines = [f"## 📁 Documents ({len(docs)} total)\n"]
    lines.append(
        f"_{len(selected_ids)} selected for context · "
        f"{'specific docs only' if selected_ids else 'all docs used by default'}_\n"
    )
    lines.append("| # | Filename | Type | In Context |")
    lines.append("|---|----------|------|------------|")
    for i, doc in enumerate(docs, 1):
        fname = doc["filename"]
        ext = fname.rsplit(".", 1)[-1].upper() if "." in fname else "?"
        sel = "✅" if str(doc["id"]) in selected_ids else "—"
        lines.append(f"| {i} | `{fname}` | `{ext}` | {sel} |")

    lines.append("\n**Manage documents:**")
    lines.append("```")
    lines.append("/select <number>      — add to chat context")
    lines.append("/select all           — select all")
    lines.append("/deselect <number>    — remove from context")
    lines.append("/deselect all         — clear all selections")
    lines.append("/delete <number>      — permanently delete")
    lines.append("```")

    await cl.Message(content="\n".join(lines)).send()


async def _handle_select(text: str):
    token = cl.user_session.get("token")
    docs = get_documents(token)
    cl.user_session.set("documents", docs)
    selected_ids = cl.user_session.get("selected_doc_ids", [])
    parts = text.split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else ""

    if not arg:
        await cl.Message(content="⚠️ Usage: `/select <number>` or `/select all`").send()
        return

    if arg == "all":
        cl.user_session.set("selected_doc_ids", [str(d["id"]) for d in docs])
        await cl.Message(
            content=f"✅ All **{len(docs)}** document(s) selected for context."
        ).send()
        return

    try:
        idx = int(arg) - 1
        if idx < 0 or idx >= len(docs):
            raise IndexError
        doc = docs[idx]
        did = str(doc["id"])
        if did not in selected_ids:
            selected_ids.append(did)
            cl.user_session.set("selected_doc_ids", selected_ids)
        await cl.Message(
            content=f"✅ `{doc['filename']}` added to context. ({len(selected_ids)} doc(s) selected)"
        ).send()
    except (ValueError, IndexError):
        await cl.Message(content="⚠️ Invalid number. Use `/docs` to see document numbers.").send()


async def _handle_deselect(text: str):
    token = cl.user_session.get("token")
    docs = get_documents(token)
    selected_ids = cl.user_session.get("selected_doc_ids", [])
    parts = text.split(maxsplit=1)
    arg = parts[1].strip().lower() if len(parts) > 1 else ""

    if not arg:
        await cl.Message(content="⚠️ Usage: `/deselect <number>` or `/deselect all`").send()
        return

    if arg == "all":
        cl.user_session.set("selected_doc_ids", [])
        await cl.Message(content="✅ All selections cleared. Chat will use **all documents**.").send()
        return

    try:
        idx = int(arg) - 1
        if idx < 0 or idx >= len(docs):
            raise IndexError
        doc = docs[idx]
        did = str(doc["id"])
        if did in selected_ids:
            selected_ids.remove(did)
            cl.user_session.set("selected_doc_ids", selected_ids)
        await cl.Message(
            content=f"✅ `{doc['filename']}` removed from context. ({len(selected_ids)} doc(s) selected)"
        ).send()
    except (ValueError, IndexError):
        await cl.Message(content="⚠️ Invalid number. Use `/docs` to see document numbers.").send()


async def _handle_delete_doc(text: str):
    token = cl.user_session.get("token")
    docs = get_documents(token)
    parts = text.split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""

    if not arg:
        await cl.Message(content="⚠️ Usage: `/delete <number>`").send()
        return

    try:
        idx = int(arg) - 1
        if idx < 0 or idx >= len(docs):
            raise IndexError
        doc = docs[idx]
        result = delete_document(token, str(doc["id"]))
        if result.get("error"):
            await cl.Message(content=f"❌ {result['error']}").send()
            return

        # Clean up selection state
        selected_ids = cl.user_session.get("selected_doc_ids", [])
        if str(doc["id"]) in selected_ids:
            selected_ids.remove(str(doc["id"]))
            cl.user_session.set("selected_doc_ids", selected_ids)

        docs = get_documents(token)
        cl.user_session.set("documents", docs)
        await cl.Message(
            content=f"🗑 `{doc['filename']}` deleted. **{len(docs)}** document(s) remaining."
        ).send()
    except (ValueError, IndexError):
        await cl.Message(content="⚠️ Invalid number. Use `/docs` to see document numbers.").send()


# ────────────────────────────────────────────────
# Chat history
# ────────────────────────────────────────────────
async def _show_history():
    token = cl.user_session.get("token")
    sessions = get_chat_sessions(token)

    if not sessions:
        await cl.Message(
            content=(
                "🗂 **No previous chat sessions found.**\n\n"
                "Start chatting to create your first session."
            )
        ).send()
        return

    today = datetime.now().date()
    by_date: dict = {}
    for s in sessions:
        try:
            last = datetime.fromisoformat(s["last_message"].replace("Z", "+00:00"))
            dk = last.date()
            if dk == today:
                label = "Today"
            elif (today - dk).days == 1:
                label = "Yesterday"
            else:
                label = dk.strftime("%d %b %Y")
        except Exception:
            label = "Other"
        by_date.setdefault(label, []).append(s)

    lines = [f"## 📜 Chat History ({len(sessions)} sessions)\n"]
    counter = 1
    session_map = {}

    for label in sorted(by_date, key=lambda x: (x not in ["Today", "Yesterday"], x), reverse=True):
        lines.append(f"**{label}**")
        lines.append("| # | Session ID | Last Active |")
        lines.append("|---|-----------|-------------|")
        for s in by_date[label]:
            sid = s["session_id"]
            session_map[counter] = sid
            try:
                last_str = datetime.fromisoformat(
                    s["last_message"].replace("Z", "+00:00")
                ).strftime("%H:%M")
            except Exception:
                last_str = "—"
            lines.append(f"| {counter} | `{sid[:16]}…` | {last_str} |")
            counter += 1
        lines.append("")

    lines.append("**Commands:**")
    lines.append("```")
    lines.append("/load <number>           — restore a past session")
    lines.append("/deletesession <number>  — delete a session")
    lines.append("```")

    cl.user_session.set("_session_map", session_map)
    await cl.Message(content="\n".join(lines)).send()


async def _handle_load_session(text: str):
    token = cl.user_session.get("token")
    session_map = cl.user_session.get("_session_map", {})
    parts = text.split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""

    if not arg:
        await cl.Message(content="⚠️ Usage: `/load <number>` — run `/history` first.").send()
        return

    try:
        idx = int(arg)
        session_id = session_map.get(idx)
        if not session_id:
            await cl.Message(content="⚠️ Session not found. Run `/history` first.").send()
            return

        messages = get_session_messages(token, session_id)
        cl.user_session.set("session_id", session_id)

        await cl.Message(
            content=(
                f"📂 **Session `{session_id[:16]}…` loaded** — {len(messages)} message(s).\n\n"
                f"Showing last {min(len(messages), 6)} messages:"
            )
        ).send()

        for m in messages[-6:]:
            role = m.get("role", "user")
            content = m.get("content", "")
            author = "**You**" if role == "user" else "**Velocis AI**"
            await cl.Message(content=f"{author}: {content}").send()

        await cl.Message(content="_Session restored. Continue the conversation below._").send()

    except ValueError:
        await cl.Message(content="⚠️ Invalid number. Run `/history` first.").send()


async def _handle_delete_session(text: str):
    token = cl.user_session.get("token")
    session_map = cl.user_session.get("_session_map", {})
    parts = text.split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""

    if not arg:
        await cl.Message(content="⚠️ Usage: `/deletesession <number>` — run `/history` first.").send()
        return

    try:
        idx = int(arg)
        session_id = session_map.get(idx)
        if not session_id:
            await cl.Message(content="⚠️ Session not found. Run `/history` first.").send()
            return

        result = delete_chat_session(token, session_id)
        if result.get("error"):
            await cl.Message(content=f"❌ {result['error']}").send()
        else:
            # Remove from map
            session_map.pop(idx, None)
            cl.user_session.set("_session_map", session_map)
            await cl.Message(content=f"🗑 Session `{session_id[:16]}…` deleted.").send()

    except ValueError:
        await cl.Message(content="⚠️ Invalid number. Run `/history` first.").send()


# ────────────────────────────────────────────────
# Date filter
# ────────────────────────────────────────────────
async def _handle_date_filter(text: str):
    """Usage: /datefilter 2024-01-01 2024-12-31"""
    parts = text.split()
    if len(parts) != 3:
        await cl.Message(
            content=(
                "⚠️ **Usage:** `/datefilter YYYY-MM-DD YYYY-MM-DD`\n"
                "**Example:** `/datefilter 2024-01-01 2024-12-31`"
            )
        ).send()
        return
    try:
        from datetime import date as date_cls
        start = datetime.strptime(parts[1], "%Y-%m-%d").date()
        end = datetime.strptime(parts[2], "%Y-%m-%d").date()
        if start > end:
            await cl.Message(content="⚠️ Start date must be before end date.").send()
            return
        cl.user_session.set("start_date", start.isoformat())
        cl.user_session.set("end_date", end.isoformat())
        await cl.Message(
            content=(
                f"🗓 Date filter set: **{start}** → **{end}**\n"
                f"Only documents within this range will be used in chat.\n"
                f"Use `/clearfilter` to remove."
            )
        ).send()
    except ValueError:
        await cl.Message(content="⚠️ Invalid date format. Use `YYYY-MM-DD`.").send()


# ────────────────────────────────────────────────
# Chat
# ────────────────────────────────────────────────
async def _handle_chat(text: str):
    token = cl.user_session.get("token")
    session_id = cl.user_session.get("session_id")
    selected_ids = cl.user_session.get("selected_doc_ids", [])
    start_date = cl.user_session.get("start_date")
    end_date = cl.user_session.get("end_date")

    # Build context hint
    if selected_ids:
        docs = cl.user_session.get("documents", [])
        doc_names = [d["filename"] for d in docs if str(d["id"]) in selected_ids]
        context_note = f"_{len(selected_ids)} doc(s) in context: {', '.join(f'`{n}`' for n in doc_names[:3])}{'…' if len(doc_names) > 3 else ''}_"
    else:
        context_note = "_Using all documents_"

    if start_date:
        context_note += f" · _Date: {start_date} → {end_date}_"

    msg = cl.Message(content="")
    await msg.send()

    async with cl.Step(name="Searching documents…", show_input=False):
        response = send_chat(
            token=token,
            query=text,
            session_id=session_id,
            doc_ids=selected_ids,
            start_date=start_date,
            end_date=end_date,
        )

    if response.get("error"):
        await msg.update(content=f"❌ **Error:** {response['error']}")
    elif "answer" in response:
        answer = response["answer"]
        await msg.update(content=f"{answer}\n\n{context_note}")
    else:
        await msg.update(content="⚠️ No response received from the server.")


# ────────────────────────────────────────────────
# Logout
# ────────────────────────────────────────────────
async def _handle_logout():
    username = cl.user_session.get("username", "User")
    cl.user_session.set("token", None)
    cl.user_session.set("username", None)
    cl.user_session.set("auth_step", "choose")
    cl.user_session.set("selected_doc_ids", [])
    cl.user_session.set("documents", [])
    cl.user_session.set("session_id", str(uuid.uuid4()))
    cl.user_session.set("start_date", None)
    cl.user_session.set("end_date", None)
    cl.user_session.set("_session_map", {})

    await cl.Message(
        content=(
            f"👋 **{username}** signed out successfully.\n\n"
            "Type **`login`** to sign back in or **`register`** to create an account."
        )
    ).send()


# ────────────────────────────────────────────────
# Help
# ────────────────────────────────────────────────
async def _show_help():
    username = cl.user_session.get("username", "")
    selected_ids = cl.user_session.get("selected_doc_ids", [])
    start_date = cl.user_session.get("start_date")
    end_date = cl.user_session.get("end_date")
    docs = cl.user_session.get("documents", [])

    status_lines = [
        f"**User:** `{username}`",
        f"**Documents:** {len(docs)} in library · {len(selected_ids)} selected",
        f"**Date filter:** {f'`{start_date}` → `{end_date}`' if start_date else 'None'}",
        f"**Session:** `{cl.user_session.get('session_id', '')[:16]}…`",
    ]

    await cl.Message(
        content=f"""## ⬡ Velocis AI — Command Reference

{chr(10).join(status_lines)}

---

### 📎 Uploading Files
Attach files to **any message** to upload them (max **{MAX_UPLOAD_FILES_PER_BATCH}** per batch).
Supported: `{', '.join(ALLOWED_EXTENSIONS)}`

---

### 📁 Document Commands
| Command | Description |
|---------|-------------|
| `/docs` | List all documents with index numbers |
| `/select <n>` | Add document #n to chat context |
| `/select all` | Select all documents |
| `/deselect <n>` | Remove document #n from context |
| `/deselect all` | Clear all selections (use all docs) |
| `/delete <n>` | Permanently delete document #n |

---

### 💬 Chat & Session Commands
| Command | Description |
|---------|-------------|
| `/newchat` | Start a fresh chat session |
| `/history` | View past sessions with numbers |
| `/load <n>` | Restore session #n |
| `/deletesession <n>` | Delete session #n |

---

### 🗓 Date Filter Commands
| Command | Description |
|---------|-------------|
| `/datefilter YYYY-MM-DD YYYY-MM-DD` | Set date range filter |
| `/clearfilter` | Remove date filter |

---

### 🔐 Account
| Command | Description |
|---------|-------------|
| `/logout` | Sign out |
| `/help` | Show this reference |

---
_Just type normally to chat with your documents._"""
    ).send()

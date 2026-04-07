# Velocis Document Analyzer — Deployment Guide

A production-ready RAG (Retrieval-Augmented Generation) application with a React frontend, FastAPI backend, and PostgreSQL + pgvector database.

---

## Architecture

```
┌─────────────────┐     HTTP/REST      ┌──────────────────────┐
│  React Frontend │ ─────────────────► │  FastAPI Backend     │
│  (Nginx :3000)  │                    │  (:8000)             │
└─────────────────┘                    └──────────┬───────────┘
                                                   │
                          ┌────────────────────────┼────────────────────────┐
                          ▼                        ▼                        ▼
               ┌──────────────────┐   ┌────────────────────┐  ┌────────────────────┐
               │  PostgreSQL      │   │  HuggingFace       │  │  LLM Provider      │
               │  + pgvector      │   │  Embeddings        │  │  (vLLM / OpenAI /  │
               │  (:5432)         │   │  (all-mpnet-base)  │  │   Gemini / Ollama) │
               └──────────────────┘   └────────────────────┘  └────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Axios, react-markdown, react-dropzone |
| Backend | FastAPI (async), LangChain, Pydantic Settings |
| Database | PostgreSQL 16 + pgvector extension |
| Embeddings | HuggingFace `all-mpnet-base-v2` (GPU-accelerated) |
| LLM Engines | vLLM (on-prem), OpenAI, Google Gemini, Ollama |
| Container | Docker + Docker Compose |
| Web Server | Nginx (serves React build) |

---

## Supported File Formats

PDF, DOC, DOCX, XLSX, CSV, PPT, PPTX, TXT, PY, MD

---

## Quick Start (Docker — Recommended)

### Prerequisites
- Docker Desktop 24+ with Docker Compose v2
- 8 GB RAM minimum (16 GB recommended for local embeddings)

### Step 1 — Clone and configure

```bash
git clone <your-repo-url>
cd vel_chatbot

# Copy the example env file
cp .env.example .env
```

Edit `.env` and set at minimum:
```env
POSTGRES_PASSWORD=your_strong_password
JWT_SECRET_KEY=your-long-random-secret-string
```

### Step 2 — Choose your LLM provider

#### Option A: On-Premise vLLM (recommended for no usage costs)
```env
LLM_PROVIDER=ONPREM
ON_PREM_MODEL_URL=http://your-vllm-server:8001/v1
ON_PREM_MODEL_NAME=gpt-oss-20b
```

#### Option B: OpenAI
```env
LLM_PROVIDER=OPENAI
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
```

#### Option C: Google Gemini
```env
LLM_PROVIDER=GEMINI
LLM_MODEL=gemini-2.5-flash-lite
GEMINI_API_KEY=AIza...
```

#### Option D: Ollama (local)
```env
LLM_PROVIDER=OLLAMA
LLM_MODEL=llama3
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Step 3 — Build and run

```bash
docker compose up --build -d
```

This starts three containers:
- `db` — PostgreSQL with pgvector
- `backend` — FastAPI on port 8000
- `frontend` — React app served by Nginx on port 3000

### Step 4 — Open the app

```
http://localhost:3000
```

Register a new account and start uploading documents.

---

## On-Premise vLLM Setup

If you are serving `gpt-oss-20b` (or any model) on your own server using vLLM:

### Install vLLM on your GPU server

```bash
pip install vllm
```

### Start the vLLM server

```bash
python -m vllm.entrypoints.openai.api_server \
  --model /path/to/gpt-oss-20b \
  --host 0.0.0.0 \
  --port 8001 \
  --served-model-name gpt-oss-20b \
  --tensor-parallel-size 2   # adjust to your GPU count
```

vLLM exposes an OpenAI-compatible API at `http://<server-ip>:8001/v1`.

### Configure the backend

```env
LLM_PROVIDER=ONPREM
ON_PREM_MODEL_URL=http://<server-ip>:8001/v1
ON_PREM_MODEL_NAME=gpt-oss-20b
```

No API key is required — vLLM accepts any string as the key.

---

## Local Development (without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

pip install -r ../requirements_new.txt

# Make sure PostgreSQL is running with pgvector enabled
# Then run:
uvicorn main:app --reload --port 8000
```

### Frontend (React)

```bash
cd frontend-react
npm install
npm start          # Runs on http://localhost:3000
```

The React dev server proxies API calls to `http://localhost:8000` automatically.

### Legacy Streamlit Frontend

```bash
cd frontend
streamlit run app.py
```

---

## Database Setup (manual / first run)

If running without Docker, initialize the database manually:

```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE chatbot;
\c chatbot
CREATE EXTENSION IF NOT EXISTS vector;
```

The FastAPI app auto-creates all tables on startup via SQLAlchemy.

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_DB` | `chatbot` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | — | **Required.** Database password |
| `LLM_PROVIDER` | `ONPREM` | `ONPREM`, `OPENAI`, `GEMINI`, or `OLLAMA` |
| `LLM_MODEL` | `gpt-oss-20b` | Model name (for OPENAI/GEMINI providers) |
| `ON_PREM_MODEL_URL` | `http://localhost:8001/v1` | vLLM server base URL |
| `ON_PREM_MODEL_NAME` | `gpt-oss-20b` | Model name served by vLLM |
| `OPENAI_API_KEY` | — | Required for `OPENAI` provider |
| `GEMINI_API_KEY` | — | Required for `GEMINI` provider |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `JWT_SECRET_KEY` | — | **Required.** Secret for JWT signing |
| `VITE_API_URL` | `/api` | Backend URL visible from the browser. Use `/api` when the frontend is served by the bundled Nginx proxy |

---

## Docker Commands Reference

```bash
# Start all services
docker compose up -d

# Rebuild after code changes
docker compose up --build -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop all services
docker compose down

# Stop and remove volumes (wipes database)
docker compose down -v

# Scale backend (if needed)
docker compose up -d --scale backend=2
```

---

## Production Deployment Notes

1. **Change secrets** — Set strong values for `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` in `.env`
2. **HTTPS** — Place a reverse proxy (Nginx/Traefik/Caddy) in front with SSL termination
3. **CORS** — Set `CORS_ALLOW_ORIGINS` in `.env` to your production frontend origin if you call the backend directly
4. **React API URL** — Set `VITE_API_URL` before building. In the bundled Docker/Nginx deployment, `/api` is the safest default
5. **Embedding cache** — The `model_cache` Docker volume persists the HuggingFace model download between restarts
6. **GPU for embeddings** — Add `deploy.resources.reservations.devices` to the backend service in `docker-compose.yaml` to pass through a GPU

---

## Project Structure

```
vel_chatbot/
├── backend/
│   ├── main.py                  # FastAPI app, all endpoints
│   ├── config.py                # Pydantic settings, reads .env
│   ├── database.py              # SQLAlchemy models & async DB helpers
│   └── services/
│       ├── llm_factory.py       # Provider switcher (ONPREM/OPENAI/GEMINI/OLLAMA)
│       ├── llm_client.py        # RAG chain with chat history
│       ├── ingestor_new.py      # Document parsing & chunking
│       └── retriever.py         # pgvector similarity search
├── frontend-react/              # React 18 frontend
│   ├── src/
│   │   ├── App.js               # Root component, state management
│   │   ├── api/client.js        # Axios API layer
│   │   ├── hooks/useAuth.js     # Auth state with localStorage
│   │   └── components/
│   │       ├── AuthPage.jsx     # Login / Register
│   │       ├── DocumentPanel.jsx # Upload + document list
│   │       ├── ChatPanel.jsx    # Chat UI with markdown rendering
│   │       └── HistoryPanel.jsx # Day-grouped chat history
│   └── package.json
├── frontend/
│   └── app.py                   # Legacy Streamlit UI (still functional)
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yaml
├── nginx.conf
├── .env.example
└── README_NEW.md
```

1. Updated System Architecture Diagram
2. Project Documentation: README.md
Markdown
# 📄 Local RAG Chatbot: Multi-Provider Document Q&A

This project is a modular, high-performance RAG (Retrieval-Augmented Generation) application built with **FastAPI**, **Streamlit**, and **PostgreSQL (pgvector)**. It supports GPU-accelerated local embeddings and allows switching between local (Ollama) and cloud (OpenAI/Gemini) LLM providers via configuration.

---

## 🛠️ Technical Stack
| Layer | Technology |
| :--- | :--- |
| **Backend** | FastAPI (Async support) |
| **Frontend** | Streamlit (Interactive Chat & Doc Management) |
| **Database** | PostgreSQL + `pgvector` extension |
| **Orchestration** | LangChain & Pydantic Settings |
| **Embeddings** | HuggingFace `sentence-transformers` (CUDA/GPU support) |
| **LLM Engines** | Ollama (Local), OpenAI GPT-4, Google Gemini |

---

## 🚀 Key Features
- **GPU-Accelerated**: Detects NVIDIA GPUs automatically for fast embedding generation.
- **Provider Switching**: Change your LLM from Llama-3 to Gemini or GPT-4o in one line within `.env`.
- **Metadata Filtering**: Query against all data or filter by **specific documents** and **date ranges**.
- **Source Citations**: View exactly which document chunks were used to generate the answer.

---

## ⚙️ Installation & Setup

### 1. Environment Configuration
Create a `.env` file in the root directory:
```env
# Database Settings
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/rag_db

# Provider Selection: OLLAMA, OPENAI, or GEMINI
LLM_PROVIDER=OLLAMA
LLM_MODEL=llama3  # e.g., gpt-4o, gemini-1.5-flash, llama3

# API Keys (Required for Cloud Providers)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Local Provider Settings
OLLAMA_BASE_URL=http://localhost:11434
2. Install Dependencies
Ensure you have Python 3.10+ and run:

Bash
pip install -r requirements.txt
3. Initialize Database
Ensure pgvector is enabled on your PostgreSQL instance:

SQL
CREATE EXTENSION IF NOT EXISTS vector;
4. Running the Application
Backend:

Bash
uvicorn backend.main:app --reload --port 8000
Frontend:

Bash
streamlit run frontend/app.py
📖 Usage Workflow
Upload: Use the Streamlit sidebar to upload PDF files. They are automatically chunked and stored.

Filter: Select specific documents or a date range from the sidebar if you want focused answers.

Chat: Enter your question in the chat bar. The assistant will retrieve relevant context and cite its sources.

# 🤖 Vel Chatbot Project Documentation

## 📂 Project Structure
```text
vel_chatbot/
├── backend/
│   ├── main.py             # FastAPI entry point
│   ├── config.py           # Configuration & .env loader
│   ├── services/
│   │   ├── llm_factory.py  # Logic to switch between Gemini/GPT/Ollama
│   │   └── llm_client.py   # RAG chain logic
│   └── .env                # Local secrets (Database URLs, API Keys)
├── frontend/
│   └── app.py              # Streamlit interface
└── README.md               # User setup guide
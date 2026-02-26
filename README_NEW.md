# 🤖 Vel RAG Chatbot: Enterprise-Grade Multi-Format Document Q&A

A production-ready RAG (Retrieval-Augmented Generation) application with **conversational memory**, **multi-format document support**, and **GPU-accelerated embeddings**. Built with FastAPI, Streamlit, and PostgreSQL (pgvector).

---

## ✨ Key Features

### 📄 Multi-Format Document Support
- **Supported Formats**: PDF, DOC, DOCX, XLSX, CSV, PPT, PPTX
- **Batch Upload**: Upload multiple documents simultaneously
- **Smart Extraction**: Automatic text extraction optimized per format

### 💬 Conversational Memory
- **Context-Aware Responses**: Maintains conversation history across messages
- **Multi-Session Support**: Create and manage multiple chat threads
- **Session Persistence**: Chat history stored in PostgreSQL

### 🎯 Advanced Filtering
- **Document-Specific Search**: Filter responses by selected documents
- **Date Range Filtering**: Query documents within specific time periods
- **Hybrid Filtering**: Combine document and date filters

### 🗑️ Document Management
- **Delete Documents**: Remove documents and automatically clean up database entries
- **View Metadata**: Track upload dates and file types
- **Source Citations**: View exact document chunks used in responses

### 🚀 Performance & Scalability
- **GPU Acceleration**: Automatic NVIDIA GPU detection for embeddings
- **Async Architecture**: FastAPI async endpoints for high concurrency
- **Vector Search**: pgvector for efficient similarity search

### 🔄 Provider Flexibility
- **Local LLM**: Ollama (Llama-3, Mistral, etc.)
- **Cloud LLMs**: OpenAI GPT-4, Google Gemini
- **Easy Switching**: Change providers via `.env` configuration

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| **Backend API** | FastAPI (Async) |
| **Frontend** | Streamlit |
| **Database** | PostgreSQL + pgvector |
| **Embeddings** | sentence-transformers (CUDA/GPU) |
| **LLM Framework** | LangChain |
| **Document Processing** | pypdf, python-docx, openpyxl, python-pptx |
| **LLM Providers** | Ollama, OpenAI, Google Gemini |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- (Optional) NVIDIA GPU with CUDA for accelerated embeddings
- (Optional) Ollama for local LLM

### 1. Clone Repository
```bash
git clone <repository-url>
cd vel_chatbot
```

### 2. Install Dependencies
```bash
pip install -r requirements_new.txt
```

### 3. Setup PostgreSQL with pgvector
```sql
CREATE DATABASE chatbot;
\c chatbot
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. Configure Environment
Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/chatbot

# LLM Provider (OLLAMA, OPENAI, or GEMINI)
LLM_PROVIDER=OLLAMA
LLM_MODEL=llama3

# API Keys (for cloud providers)
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here

# Ollama Settings (for local)
OLLAMA_BASE_URL=http://localhost:11434
```

### 5. Initialize Database
The database tables will be created automatically on first run.

---

## 🚀 Running the Application

### Start Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
streamlit run app_new.py
```

Access the application at: **http://localhost:8501**

---

## 📖 Usage Guide

### 1. Upload Documents
- Click **"Upload Documents"** in the sidebar
- Select multiple files (PDF, DOCX, XLSX, CSV, PPTX)
- Click **"📤 Upload All"**
- Documents are automatically processed and indexed

### 2. Start Chatting
- Type your question in the chat input
- The assistant retrieves relevant context and responds
- View source citations by expanding **"📄 View Sources"**

### 3. Filter Responses
- **By Document**: Select specific documents from the sidebar
- **By Date**: Enable date filter and set date range
- Filters apply to all subsequent queries

### 4. Manage Chat Sessions
- Click **"➕ New Chat"** to start a fresh conversation
- Each session maintains independent conversation history
- Previous context is automatically included in responses

### 5. Delete Documents
- Click **🗑️** next to any document in the sidebar
- Document and all associated chunks are removed from database

---

## 🏗️ Project Structure

```
vel_chatbot/
├── backend/
│   ├── main.py                    # FastAPI app with all endpoints
│   ├── config.py                  # Environment configuration
│   ├── database.py                # SQLAlchemy models & DB operations
│   ├── services/
│   │   ├── ingestor_new.py       # Multi-format document processing
│   │   ├── retriever.py          # Vector similarity search
│   │   ├── llm_client.py         # LLM integration with memory
│   │   └── llm_factory.py        # Provider switching logic
│   └── .env                       # Configuration (not in repo)
├── frontend/
│   └── app_fixed.py                 # Enhanced Streamlit UI
├── requirements_new.txt           # Python dependencies
└── README.md                      # This file
```

---

## 🔧 API Endpoints

### Documents
- `POST /upload-documents/` - Upload multiple documents
- `GET /documents/` - List all documents
- `DELETE /documents/{document_id}` - Delete document

### Chat
- `POST /chat/` - Send query with session context
  ```json
  {
    "query": "What is the main topic?",
    "session_id": "uuid",
    "document_ids": ["uuid1", "uuid2"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
  ```

---

## 🎨 UI Features

### Modern Design
- Gradient headers and smooth animations
- Responsive layout with sidebar navigation
- Color-coded document cards
- Interactive hover effects

### User Experience
- Real-time upload progress
- Inline document deletion
- Expandable source citations
- Session ID display for tracking

---

## 🔐 Security Best Practices

- Store API keys in `.env` (never commit)
- Use environment variables for sensitive data
- Implement authentication for production deployment
- Sanitize user inputs before processing

---

## 🚀 Performance Optimization

### GPU Acceleration
The system automatically detects NVIDIA GPUs:
```python
device = "cuda" if torch.cuda.is_available() else "cpu"
```

### Batch Processing
- Documents are chunked and embedded in batches
- Reduces processing time for large documents

### Async Operations
- All database operations are async
- Non-blocking API endpoints for better concurrency

---

## 🐛 Troubleshooting

### Backend won't start
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Ensure pgvector extension is installed

### Documents not uploading
- Check file format is supported
- Verify file size limits
- Check backend logs for errors

### Chat responses are slow
- For local LLM: Ensure Ollama is running
- For cloud LLM: Check API key validity
- Consider using GPU for embeddings

### No GPU detected
- Install CUDA toolkit
- Verify PyTorch CUDA installation: `torch.cuda.is_available()`

---

## 📊 Database Schema

### Documents Table
```sql
id          UUID PRIMARY KEY
filename    VARCHAR
file_type   VARCHAR
uploaded_at DATE
```

### Document Chunks Table
```sql
id          UUID PRIMARY KEY
document_id UUID FOREIGN KEY
content     TEXT
embedding   VECTOR(384)
uploaded_at TIMESTAMP
```

### Chat History Table
```sql
id          UUID PRIMARY KEY
session_id  UUID
role        VARCHAR (user/assistant)
content     TEXT
created_at  TIMESTAMP
```

---

## 🔄 Switching LLM Providers

Edit `.env` file:

### For Ollama (Local)
```env
LLM_PROVIDER=OLLAMA
LLM_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

### For OpenAI
```env
LLM_PROVIDER=OPENAI
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
```

### For Google Gemini
```env
LLM_PROVIDER=GEMINI
LLM_MODEL=gemini-1.5-flash
GEMINI_API_KEY=...
```

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **LangChain** for LLM orchestration
- **pgvector** for vector similarity search
- **Sentence Transformers** for embeddings
- **FastAPI** for modern async API framework
- **Streamlit** for rapid UI development

---

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Built with ❤️ for enterprise-grade document intelligence**

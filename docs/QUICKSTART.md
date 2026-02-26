# 🚀 Quick Start Guide - Vel Chatbot

Get your enhanced RAG chatbot running in 5 minutes!

---

## ⚡ Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.10 or higher
- [ ] PostgreSQL 14+ installed and running
- [ ] pgvector extension available
- [ ] (Optional) NVIDIA GPU with CUDA for faster embeddings
- [ ] (Optional) Ollama installed for local LLM

---

## 📦 Step 1: Install Dependencies (2 min)

```bash
# Navigate to project directory
cd vel_chatbot

# Install Python packages
pip install -r requirements_new.txt

# Verify installation
python -c "import fastapi, streamlit, sqlalchemy; print('✅ Dependencies installed')"
```

---

## 🗄️ Step 2: Setup Database (2 min)

### Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# In psql:
CREATE DATABASE chatbot;
\c chatbot
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Run Migration Script
```bash
psql -U postgres -d chatbot -f backend/migration.sql
```

**Expected Output:**
```
✅ Migration completed successfully!
```

---

## ⚙️ Step 3: Configure Environment (1 min)

Create `backend/.env` file:

```bash
cd backend
```

**For Local LLM (Ollama):**
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/chatbot
LLM_PROVIDER=OLLAMA
LLM_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

**For OpenAI:**
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/chatbot
LLM_PROVIDER=OPENAI
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-your-key-here
```

**For Google Gemini:**
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/chatbot
LLM_PROVIDER=GEMINI
LLM_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your-key-here
```

---

## 🚀 Step 4: Start Application (30 sec)

### Terminal 1 - Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
🚀 Database tables initialized successfully.
```

### Terminal 2 - Frontend
```bash
cd frontend
streamlit run app_new.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

---

## ✅ Step 5: Verify Installation (30 sec)

### Test Backend
Open browser: http://localhost:8000/docs

You should see FastAPI Swagger UI with endpoints:
- POST /upload-documents/
- GET /documents/
- POST /chat/
- DELETE /documents/{document_id}

### Test Frontend
Open browser: http://localhost:8501

You should see:
- 🤖 Vel RAG Chatbot header
- Sidebar with upload section
- Chat interface

---

## 🎯 Quick Test

### 1. Upload a Document
- Click "Upload Documents" in sidebar
- Select a PDF or DOCX file
- Click "📤 Upload All"
- Wait for success message

### 2. Ask a Question
- Type a question in chat input
- Press Enter
- View response with source citations

### 3. Start New Chat
- Click "➕ New Chat" in sidebar
- Ask another question
- Verify independent conversation

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install -r requirements_new.txt
```

**Error:** `could not connect to server`
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS
```

**Error:** `relation "documents" does not exist`
```bash
# Run migration script
psql -U postgres -d chatbot -f backend/migration.sql
```

### Frontend won't start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`
```bash
pip install streamlit
```

**Error:** `Connection refused to localhost:8000`
- Ensure backend is running first
- Check backend terminal for errors

### Upload fails

**Error:** `Unsupported file type`
- Verify file extension is: pdf, doc, docx, xlsx, csv, ppt, pptx
- Check file is not corrupted

**Error:** `Failed to process document`
```bash
# Install missing dependencies
pip install python-docx openpyxl python-pptx
```

### Chat not working

**Error:** `session_id required`
- This is normal - frontend handles this automatically
- If persists, clear browser cache and refresh

**Error:** `Ollama connection refused`
```bash
# Start Ollama
ollama serve

# In another terminal, pull model
ollama pull llama3
```

---

## 🎨 Using the Application

### Upload Multiple Documents
1. Click "Upload Documents"
2. Select multiple files (Ctrl+Click or Cmd+Click)
3. Click "📤 Upload All"
4. Wait for confirmation

### Filter by Documents
1. In sidebar, find "📚 Uploaded Documents"
2. Use "Filter by documents" dropdown
3. Select one or more documents
4. All queries will only search selected documents

### Filter by Date
1. Check "Enable date filter"
2. Set "From" and "To" dates
3. Queries will only search documents in date range

### Delete Documents
1. Find document in sidebar
2. Click 🗑️ button
3. Document and all chunks removed from database

### Manage Chat Sessions
1. Click "➕ New Chat" to start fresh conversation
2. Each session has independent history
3. Session ID shown at bottom of sidebar

### View Sources
1. After receiving answer
2. Click "📄 View Sources" expander
3. See exact document chunks used

---

## 📊 System Requirements

### Minimum:
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- Python: 3.10+
- PostgreSQL: 14+

### Recommended:
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB SSD
- GPU: NVIDIA with 4GB+ VRAM
- Python: 3.11+
- PostgreSQL: 15+

---

## 🔧 Configuration Options

### Adjust Chunk Size
Edit `backend/services/ingestor_new.py`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Increase for longer chunks
    chunk_overlap=50,  # Increase for more context
)
```

### Change Embedding Model
Edit `backend/services/ingestor_new.py`:
```python
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"  # Better quality
# Note: Update Vector dimension in database.py to match
```

### Adjust Chat History Length
Edit `backend/database.py`:
```python
async def get_chat_history(session_id: uuid.UUID, limit: int = 20):  # Increase limit
```

---

## 📈 Performance Tips

### For Faster Embeddings:
- Use GPU (automatic if CUDA available)
- Use smaller embedding model
- Process documents in batches

### For Faster Chat:
- Use local LLM (Ollama)
- Reduce chunk_size
- Limit chat history length

### For Better Answers:
- Use larger embedding model
- Increase chunk_size
- Use GPT-4 or Gemini Pro

---

## 🎓 Next Steps

1. **Read Full Documentation**: Check `README_NEW.md`
2. **Explore API**: Visit http://localhost:8000/docs
3. **Customize UI**: Edit `frontend/app_new.py`
4. **Add Authentication**: Implement JWT tokens
5. **Deploy to Production**: Use Docker + nginx

---

## 📞 Getting Help

### Check Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Database logs
tail -f /var/log/postgresql/postgresql-15-main.log
```

### Test Database Connection
```bash
psql -U postgres -d chatbot -c "SELECT COUNT(*) FROM documents;"
```

### Verify Environment
```bash
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

---

## ✅ Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 8501
- [ ] Can upload PDF document
- [ ] Can upload DOCX document
- [ ] Can ask questions and get answers
- [ ] Can see source citations
- [ ] Can delete documents
- [ ] Can create new chat sessions
- [ ] Filters work correctly

---

## 🎉 You're Ready!

Your enhanced RAG chatbot is now running with:
- ✅ Multi-format document support
- ✅ Conversational memory
- ✅ Modern UI
- ✅ Document management
- ✅ Advanced filtering

**Start uploading documents and asking questions!**

---

**Need more help?** Check:
- `README_NEW.md` - Full documentation
- `MIGRATION_GUIDE.md` - Upgrade instructions
- `IMPLEMENTATION_SUMMARY.md` - Technical details

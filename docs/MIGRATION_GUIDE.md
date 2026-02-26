# 🔄 Migration Guide: Upgrading Vel Chatbot

## Overview
This guide helps you migrate from the basic version to the enhanced enterprise version with multi-format support, chat history, and improved UI.

---

## 📋 Changes Summary

### Database Changes
1. **Documents table**: Added `file_type` column
2. **New table**: `chat_history` for conversation memory
3. **Cascade delete**: Automatic cleanup of chunks when document is deleted

### Backend Changes
1. **Multi-document upload**: `/upload-documents/` endpoint (replaces `/upload-document/`)
2. **Delete endpoint**: `/documents/{id}` DELETE method
3. **Chat with sessions**: `session_id` required in chat requests
4. **Multi-format support**: New document processor

### Frontend Changes
1. **Batch upload**: Multiple file selection
2. **Delete buttons**: Per-document deletion
3. **Chat sessions**: New chat thread management
4. **Enhanced UI**: Modern styling and animations

---

## 🚀 Migration Steps

### Step 1: Backup Current Database
```bash
pg_dump -U postgres chatbot > backup_chatbot.sql
```

### Step 2: Update Database Schema

Run these SQL commands:

```sql
-- Add file_type column to documents table
ALTER TABLE documents ADD COLUMN file_type VARCHAR;

-- Update existing records (assuming all are PDFs)
UPDATE documents SET file_type = 'pdf' WHERE file_type IS NULL;

-- Make file_type NOT NULL
ALTER TABLE documents ALTER COLUMN file_type SET NOT NULL;

-- Create chat_history table
CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_chat_history_session ON chat_history(session_id);
CREATE INDEX idx_chat_history_created ON chat_history(created_at);
```

### Step 3: Install New Dependencies
```bash
pip install python-docx==1.1.2 openpyxl==3.1.5 python-pptx==1.0.2
```

Or use the new requirements file:
```bash
pip install -r requirements_new.txt
```

### Step 4: Update Backend Files

Replace or rename files:
```bash
# Backup old files
cp backend/services/ingestor.py backend/services/ingestor_old.py
cp backend/main.py backend/main_old.py
cp frontend/app.py frontend/app_old.py

# Use new files
cp backend/services/ingestor_new.py backend/services/ingestor.py
# Update main.py with new endpoints (see main.py changes)
cp frontend/app_new.py frontend/app.py
```

### Step 5: Update Environment Variables

No changes needed to `.env` file - all existing variables remain compatible.

### Step 6: Test Migration

1. **Start backend**:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. **Verify endpoints**:
```bash
curl http://localhost:8000/documents/
```

3. **Start frontend**:
```bash
cd frontend
streamlit run app.py
```

4. **Test features**:
   - Upload a PDF (should work as before)
   - Upload a DOCX file (new feature)
   - Try deleting a document
   - Start a new chat session

---

## 🔍 Verification Checklist

- [ ] Database schema updated successfully
- [ ] All existing documents visible in UI
- [ ] Can upload PDF files
- [ ] Can upload DOCX, XLSX, CSV, PPTX files
- [ ] Can delete documents
- [ ] Chat responses include history context
- [ ] New chat button creates fresh session
- [ ] Source citations display correctly
- [ ] Date and document filters work

---

## ⚠️ Breaking Changes

### API Changes

**Old Upload Endpoint**:
```python
POST /upload-document/
# Single file only
```

**New Upload Endpoint**:
```python
POST /upload-documents/
# Multiple files supported
```

**New Chat Request**:
```python
{
  "query": "...",
  "session_id": "uuid",  # NEW: Required
  "document_ids": [...],
  "start_date": "...",
  "end_date": "..."
}
```

### Frontend Changes

If you have custom frontend code:
- Update API calls to use `/upload-documents/`
- Add `session_id` to chat requests
- Handle `file_type` in document metadata

---

## 🐛 Rollback Procedure

If you need to rollback:

### 1. Restore Database
```bash
psql -U postgres chatbot < backup_chatbot.sql
```

### 2. Restore Old Files
```bash
cp backend/services/ingestor_old.py backend/services/ingestor.py
cp backend/main_old.py backend/main.py
cp frontend/app_old.py frontend/app.py
```

### 3. Restart Services
```bash
# Terminal 1
uvicorn backend.main:app --reload

# Terminal 2
streamlit run frontend/app.py
```

---

## 📊 Performance Considerations

### Before Migration
- Single document upload
- No chat history overhead
- Simple queries

### After Migration
- Batch document processing (may take longer)
- Chat history lookups (minimal overhead with indexes)
- Conversational context (slightly larger prompts)

**Recommendation**: Monitor database size and add indexes if needed:
```sql
CREATE INDEX idx_document_chunks_doc_id ON document_chunks(document_id);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at);
```

---

## 🆘 Common Issues

### Issue: "column file_type does not exist"
**Solution**: Run the ALTER TABLE command from Step 2

### Issue: Chat history not working
**Solution**: Verify chat_history table exists:
```sql
SELECT * FROM chat_history LIMIT 1;
```

### Issue: Document upload fails for DOCX
**Solution**: Install python-docx:
```bash
pip install python-docx==1.1.2
```

### Issue: Old documents show no file_type
**Solution**: Update existing records:
```sql
UPDATE documents SET file_type = 'pdf' WHERE file_type IS NULL OR file_type = '';
```

---

## 📈 Post-Migration Optimization

### 1. Vacuum Database
```sql
VACUUM ANALYZE documents;
VACUUM ANALYZE document_chunks;
VACUUM ANALYZE chat_history;
```

### 2. Monitor Performance
```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. Clean Old Sessions (Optional)
```sql
-- Delete chat history older than 30 days
DELETE FROM chat_history 
WHERE created_at < NOW() - INTERVAL '30 days';
```

---

## ✅ Success Criteria

Migration is successful when:
1. All existing documents are accessible
2. New document formats can be uploaded
3. Chat maintains conversation context
4. Document deletion works correctly
5. No errors in backend logs
6. UI loads without issues

---

## 📞 Support

If you encounter issues:
1. Check backend logs: `uvicorn main:app --log-level debug`
2. Check database connections
3. Verify all dependencies installed
4. Review this migration guide
5. Check README_NEW.md for detailed documentation

---

**Migration Time Estimate**: 15-30 minutes (depending on database size)

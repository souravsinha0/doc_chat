-- Migration Script for Vel Chatbot Enhancement
-- Run this script to upgrade your database schema

-- ============================================
-- STEP 1: Add file_type column to documents
-- ============================================

-- Add the column (allow NULL temporarily)
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_type VARCHAR;

-- Update existing records (assuming all are PDFs)
UPDATE documents 
SET file_type = 'pdf' 
WHERE file_type IS NULL OR file_type = '';

-- Make the column NOT NULL
ALTER TABLE documents ALTER COLUMN file_type SET NOT NULL;

-- ============================================
-- STEP 2: Create chat_history table
-- ============================================

CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- ============================================
-- STEP 3: Create indexes for performance
-- ============================================

-- Index for chat history queries by session
CREATE INDEX IF NOT EXISTS idx_chat_history_session 
ON chat_history(session_id);

-- Index for chat history queries by time
CREATE INDEX IF NOT EXISTS idx_chat_history_created 
ON chat_history(created_at DESC);

-- Index for document chunks by document_id (if not exists)
CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id 
ON document_chunks(document_id);

-- Index for documents by upload date
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at 
ON documents(uploaded_at DESC);

-- ============================================
-- STEP 4: Verify migration
-- ============================================

-- Check documents table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'documents';

-- Check chat_history table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'chat_history';

-- Check indexes
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- ============================================
-- STEP 5: Verify data integrity
-- ============================================

-- Count documents
SELECT COUNT(*) as total_documents FROM documents;

-- Check for any NULL file_types (should be 0)
SELECT COUNT(*) as null_file_types 
FROM documents 
WHERE file_type IS NULL;

-- Show sample documents
SELECT id, filename, file_type, uploaded_at 
FROM documents 
LIMIT 5;

-- ============================================
-- OPTIONAL: Cleanup old data
-- ============================================

-- Uncomment to delete chat history older than 90 days
-- DELETE FROM chat_history 
-- WHERE created_at < NOW() - INTERVAL '90 days';

-- ============================================
-- OPTIONAL: Performance optimization
-- ============================================

-- Analyze tables for query optimization
ANALYZE documents;
ANALYZE document_chunks;
ANALYZE chat_history;

-- Vacuum to reclaim space
VACUUM ANALYZE documents;
VACUUM ANALYZE document_chunks;
VACUUM ANALYZE chat_history;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration completed successfully!';
    RAISE NOTICE 'Documents table: file_type column added';
    RAISE NOTICE 'Chat history table: created';
    RAISE NOTICE 'Indexes: created for performance';
    RAISE NOTICE 'Next step: Update application code and restart services';
END $$;

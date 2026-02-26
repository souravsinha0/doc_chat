-- ==========================================
-- Chatbot Database Schema
-- ==========================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- USERS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    
    CONSTRAINT users_email_key UNIQUE (email),
    CONSTRAINT users_username_key UNIQUE (username)
);

CREATE INDEX IF NOT EXISTS idx_users_email
    ON public.users (email);

CREATE INDEX IF NOT EXISTS idx_users_username
    ON public.users (username);

-- ==========================================
-- DOCUMENTS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY,
    filename VARCHAR NOT NULL,
    uploaded_at DATE NOT NULL,
    file_type VARCHAR NOT NULL,
    user_id UUID NOT NULL,
    
    CONSTRAINT fk_documents_user
        FOREIGN KEY (user_id)
        REFERENCES public.users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at
    ON public.documents (uploaded_at DESC);

CREATE INDEX IF NOT EXISTS idx_documents_user_id
    ON public.documents (user_id);

-- ==========================================
-- DOCUMENT CHUNKS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID,
    content TEXT,
    embedding vector(768),
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT document_chunks_document_id_fkey
        FOREIGN KEY (document_id)
        REFERENCES public.documents(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id
    ON public.document_chunks (document_id);

-- ==========================================
-- CHAT HISTORY TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS public.chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    user_id UUID NOT NULL,
    
    CONSTRAINT chat_history_role_check
        CHECK (role IN ('user', 'assistant')),
        
    CONSTRAINT fk_chat_history_user
        FOREIGN KEY (user_id)
        REFERENCES public.users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_history_created
    ON public.chat_history (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_history_session
    ON public.chat_history (session_id);

CREATE INDEX IF NOT EXISTS idx_chat_history_user_id
    ON public.chat_history (user_id);

-- ==========================================
-- END OF FILE
-- ==========================================

-- Migration Script for Enhanced Vel Chatbot with Authentication
-- Run this script to add user authentication and update schema

-- ============================================
-- STEP 1: Create users table
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- ============================================
-- STEP 2: Add user_id to documents table
-- ============================================

-- Add user_id column (allow NULL temporarily for existing data)
ALTER TABLE documents ADD COLUMN IF NOT EXISTS user_id UUID;

-- Create a default user for existing documents (optional)
DO $$
DECLARE
    default_user_id UUID;
BEGIN
    -- Insert default user if not exists
    INSERT INTO users (username, email, hashed_password)
    VALUES ('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQvQQb9Fy')
    ON CONFLICT (username) DO NOTHING
    RETURNING id INTO default_user_id;
    
    -- Get the default user id if already exists
    IF default_user_id IS NULL THEN
        SELECT id INTO default_user_id FROM users WHERE username = 'admin';
    END IF;
    
    -- Update existing documents to belong to default user
    UPDATE documents SET user_id = default_user_id WHERE user_id IS NULL;
END $$;

-- Make user_id NOT NULL after updating existing records
ALTER TABLE documents ALTER COLUMN user_id SET NOT NULL;

-- Add foreign key constraint
ALTER TABLE documents ADD CONSTRAINT fk_documents_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ============================================
-- STEP 3: Add user_id to chat_history table
-- ============================================

-- Add user_id column (allow NULL temporarily)
ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS user_id UUID;

-- Update existing chat history to belong to default user
DO $$
DECLARE
    default_user_id UUID;
BEGIN
    SELECT id INTO default_user_id FROM users WHERE username = 'admin';
    UPDATE chat_history SET user_id = default_user_id WHERE user_id IS NULL;
END $$;

-- Make user_id NOT NULL
ALTER TABLE chat_history ALTER COLUMN user_id SET NOT NULL;

-- Add foreign key constraint
ALTER TABLE chat_history ADD CONSTRAINT fk_chat_history_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ============================================
-- STEP 4: Create indexes for performance
-- ============================================

-- Index for user lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Index for document queries by user
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);

-- Index for chat history queries by user
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);

-- ============================================
-- STEP 5: Verify migration
-- ============================================

-- Check users table
SELECT COUNT(*) as total_users FROM users;

-- Check documents have user_id
SELECT COUNT(*) as docs_with_user FROM documents WHERE user_id IS NOT NULL;

-- Check chat_history have user_id
SELECT COUNT(*) as chats_with_user FROM chat_history WHERE user_id IS NOT NULL;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration completed successfully!';
    RAISE NOTICE 'Users table: created';
    RAISE NOTICE 'Documents: user_id column added';
    RAISE NOTICE 'Chat history: user_id column added';
    RAISE NOTICE 'Indexes: created for performance';
    RAISE NOTICE '';
    RAISE NOTICE 'Default admin user created:';
    RAISE NOTICE 'Username: admin';
    RAISE NOTICE 'Password: admin123';
    RAISE NOTICE 'Please change this password after first login!';
END $$;

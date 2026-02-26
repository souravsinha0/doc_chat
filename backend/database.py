import os
import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, Date, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import settings
import asyncio

# Database connection settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1998@localhost:5432/chatbot")

# 1. Use create_async_engine
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# 2. Use async_sessionmaker and specify the class as AsyncSession
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    uploaded_at = Column(Date, default=date.today, nullable=False)
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    user = relationship("User")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False) # Use embedding dimension of your model (e.g., 1536 for OpenAI, 384 for bge-small)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    document = relationship("Document", back_populates="chunks")

# engine = create_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Corrected init_db using engine.begin() correctly
async def init_db():
    try:
        # For async engines, we use the connection within an async context
        async with engine.begin() as conn:
            # run_sync is required to bridge to the sync metadata method
            await conn.run_sync(Base.metadata.create_all)
        print("🚀 Database tables initialized successfully.")
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        raise e

# --- Database Operations ---

async def store_document_metadata(doc_id: uuid.UUID, filename: str, file_type: str, user_id: uuid.UUID):
    async with SessionLocal() as session:
        new_doc = Document(id=doc_id, filename=filename, file_type=file_type, user_id=user_id)
        session.add(new_doc)
        await session.commit()
        await session.refresh(new_doc)
        return new_doc

async def store_document_chunk(
    doc_id: uuid.UUID, 
    content: str, 
    embedding: List[float], 
    uploaded_at: datetime = datetime.utcnow()
):
    async with SessionLocal() as session:
        new_chunk = DocumentChunk(
            document_id=doc_id,
            content=content,
            embedding=embedding,
            uploaded_at=uploaded_at
        )
        session.add(new_chunk)
        await session.commit()
        await session.refresh(new_chunk)
        return new_chunk

async def get_documents_metadata(user_id: Optional[uuid.UUID] = None):
    async with SessionLocal() as session:
        if user_id:
            result = await session.execute(select(Document).where(Document.user_id == user_id))
        else:
            result = await session.execute(select(Document))
        return result.scalars().all()

async def get_document_by_id(doc_id: uuid.UUID):
    async with SessionLocal() as session:
        result = await session.execute(select(Document).where(Document.id == doc_id))
        return result.scalars().first()

async def get_document_chunks(doc_id: uuid.UUID):
    async with SessionLocal() as session:
        result = await session.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == doc_id).order_by(DocumentChunk.uploaded_at)
        )
        return result.scalars().all()

async def get_all_chunks():
    async with SessionLocal() as session:
        result = await session.execute(select(DocumentChunk))
        return result.scalars().all()

async def delete_document(doc_id: uuid.UUID):
    async with SessionLocal() as session:
        doc = await session.execute(select(Document).where(Document.id == doc_id))
        doc_obj = doc.scalars().first()
        if doc_obj:
            await session.delete(doc_obj)
            await session.commit()
            return True
        return False

async def store_chat_message(session_id: uuid.UUID, role: str, content: str, user_id: uuid.UUID):
    async with SessionLocal() as session:
        message = ChatHistory(session_id=session_id, role=role, content=content, user_id=user_id)
        session.add(message)
        await session.commit()
        return message

async def get_chat_history(session_id: uuid.UUID, user_id: uuid.UUID, limit: int = 10):
    async with SessionLocal() as session:
        result = await session.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id, ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))

async def get_all_chat_sessions(user_id: uuid.UUID):
    async with SessionLocal() as session:
        result = await session.execute(
            select(ChatHistory.session_id, func.max(ChatHistory.created_at).label('last_message'))
            .where(ChatHistory.user_id == user_id)
            .group_by(ChatHistory.session_id)
            .order_by(func.max(ChatHistory.created_at).desc())
        )
        return result.all()

async def create_user(username: str, email: str, hashed_password: str):
    async with SessionLocal() as session:
        user = User(username=username, email=email, hashed_password=hashed_password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def get_user_by_username(username: str):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalars().first()

async def get_user_by_email(email: str):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()
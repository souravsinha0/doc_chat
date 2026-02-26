from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime, timedelta
import uuid
import jwt
import logging
from passlib.context import CryptContext
from sqlalchemy import delete
from database import init_db, store_document_metadata, get_documents_metadata, delete_document, store_chat_message, get_chat_history, create_user, get_user_by_username, get_all_chat_sessions, SessionLocal, ChatHistory
from services.ingestor_new import process_document
from services.retriever import retrieve_relevant_chunks
from services.llm_client import get_chat_response

app = FastAPI(title="Vel RAG Chatbot API")
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

@app.on_event("startup")
async def startup_event():
    await init_db()

# --- Pydantic Models ---
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str

class DocumentMetadata(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str
    uploaded_at: date

class ChatRequest(BaseModel):
    query: str
    session_id: uuid.UUID
    document_ids: Optional[List[uuid.UUID]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ChatResponse(BaseModel):
    answer: str
    source_chunks: List[str]

class ChatSession(BaseModel):
    session_id: uuid.UUID
    last_message: datetime

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return uuid.UUID(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# --- Routes ---

@app.post("/register", response_model=Token)
async def register(user: UserRegister):
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = await create_user(user.username, user.email, hashed_password)
    
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=str(new_user.id),
        username=new_user.username
    )

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await get_user_by_username(user.username)
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=str(db_user.id),
        username=db_user.username
    )

@app.post("/upload-documents/", response_model=List[DocumentMetadata])
async def upload_documents(
    files: List[UploadFile] = File(...),
    user_id: uuid.UUID = Depends(get_current_user)
):
    SUPPORTED_TYPES = {'pdf', 'doc', 'docx', 'xlsx', 'csv', 'ppt', 'pptx', 'txt', 'py', 'md'}
    uploaded_docs = []
    existing_docs = await get_documents_metadata(user_id)
    existing_filenames = {doc.filename for doc in existing_docs}
    skipped = []
    
    for file in files:
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in SUPPORTED_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        if file.filename in existing_filenames:
            skipped.append(file.filename)
            continue
        
        try:
            file_content = await file.read()
            doc_id = uuid.uuid4()
            
            await store_document_metadata(doc_id, file.filename, file_ext, user_id)
            # Process synchronously instead of background task
            await process_document(doc_id, file.filename, file_content, file_ext)
            
            uploaded_docs.append(DocumentMetadata(
                id=doc_id,
                filename=file.filename,
                file_type=file_ext,
                uploaded_at=date.today()
            ))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process {file.filename}: {e}")
    
    if skipped:
        logger.info(f"Skipped {len(skipped)} duplicate files: {skipped}")
    
    return uploaded_docs

@app.get("/documents/", response_model=List[DocumentMetadata])
async def get_all_uploaded_documents(user_id: uuid.UUID = Depends(get_current_user)):
    documents = await get_documents_metadata(user_id)
    return [
        DocumentMetadata(id=doc.id, filename=doc.filename, file_type=doc.file_type, uploaded_at=doc.uploaded_at) 
        for doc in documents
    ]

@app.post("/chat/", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest, user_id: uuid.UUID = Depends(get_current_user)):
    try:
        chat_history = await get_chat_history(request.session_id, user_id, limit=10)
        history_list = [{'role': msg.role, 'content': msg.content} for msg in chat_history]

        # Add recent user turns for better retrieval on follow-up questions.
        previous_user_turns = [msg['content'] for msg in history_list if msg['role'] == 'user'][-2:]
        retrieval_query = request.query
        if previous_user_turns:
            retrieval_query = " ".join(previous_user_turns + [request.query])
        
        relevant_chunks = await retrieve_relevant_chunks(
            query=retrieval_query,
            user_id=user_id,
            document_ids=request.document_ids,
            start_date=request.start_date,
            end_date=request.end_date,
            top_k=15
        )

        context_texts = [chunk.content for chunk in relevant_chunks] if relevant_chunks else []
        logger.info(
            "Chat retrieval: user_id=%s session_id=%s chunks=%d doc_filter=%s",
            user_id,
            request.session_id,
            len(context_texts),
            bool(request.document_ids),
        )
        llm_response = await get_chat_response(request.query, context_chunks=context_texts, chat_history=history_list)
        
        await store_chat_message(request.session_id, 'user', request.query, user_id)
        await store_chat_message(request.session_id, 'assistant', llm_response, user_id)
        
        return ChatResponse(answer=llm_response, source_chunks=context_texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

@app.delete("/documents/{document_id}")
async def delete_document_endpoint(document_id: uuid.UUID, user_id: uuid.UUID = Depends(get_current_user)):
    success = await delete_document(document_id)
    if success:
        return JSONResponse(content={"message": "Document deleted successfully"})
    raise HTTPException(status_code=404, detail="Document not found")

@app.get("/chat-sessions/", response_model=List[ChatSession])
async def get_user_chat_sessions(user_id: uuid.UUID = Depends(get_current_user)):
    sessions = await get_all_chat_sessions(user_id)
    return [ChatSession(session_id=s[0], last_message=s[1]) for s in sessions]

@app.get("/chat-history/{session_id}")
async def get_session_chat_history(session_id: uuid.UUID, user_id: uuid.UUID = Depends(get_current_user)):
    messages = await get_chat_history(session_id, user_id, limit=100)
    return [{"role": msg.role, "content": msg.content, "created_at": msg.created_at.isoformat()} for msg in messages]

@app.delete("/chat-sessions/{session_id}")
async def delete_chat_session(session_id: uuid.UUID, user_id: uuid.UUID = Depends(get_current_user)):
    async with SessionLocal() as session:
        await session.execute(delete(ChatHistory).where(ChatHistory.session_id == session_id, ChatHistory.user_id == user_id))
        await session.commit()
    return {"message": "Chat session deleted"}

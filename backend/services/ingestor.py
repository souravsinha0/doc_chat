import io
import uuid
from datetime import datetime
from typing import List

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import torch

from database import store_document_chunk

# Initialize embedding model (runs on GPU if available)
# Use a smaller, efficient model for local deployment.
# For BAAI/bge-small-en-v1.5, embedding dimension is 384.
# For a larger model like BAAI/bge-large-en-v1.5, dimension is 1024.
# Make sure this matches the Vector dimension in database.py
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" # Output dim: 384
# EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5" # Output dim: 384 (needs specific install)
# EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5" # Output dim: 1024 (needs specific install)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading embedding model '{EMBEDDING_MODEL_NAME}' on {device}")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME).to(device)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False,
)

async def process_pdf_document(doc_id: uuid.UUID, filename: str, file_content: bytes):
    """
    Parses a PDF, chunks its text, generates embeddings, and stores them.
    """
    reader = PdfReader(io.BytesIO(file_content))
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    chunks = text_splitter.split_text(full_text)
    
    # Generate embeddings for all chunks in a batch (more efficient)
    # Ensure this uses the GPU if available
    embeddings: List[List[float]] = embedding_model.encode(chunks, convert_to_tensor=False).tolist() # Convert to list for pgvector

    # Store each chunk and its embedding
    current_time = datetime.utcnow()
    for i, chunk_content in enumerate(chunks):
        await store_document_chunk(
            doc_id=doc_id,
            content=chunk_content,
            embedding=embeddings[i],
            uploaded_at=current_time # All chunks from one doc share the same upload_time
        )
    print(f"Processed and stored {len(chunks)} chunks for document {filename} (ID: {doc_id})")
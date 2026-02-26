import logging
import re
import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import and_, select

from sentence_transformers.cross_encoder import CrossEncoder  # New: For advanced reranking
import torch  # New: For device detection

from database import Document, DocumentChunk, SessionLocal
from .ingestor_new import embedding_model

logger = logging.getLogger(__name__)

# New: Device detection (consistent with ingestor)
device = "cuda" if torch.cuda.is_available() else "cpu"

# New: Load Cross-Encoder for reranking (better than simple lexical overlap)
# Use a model trained for relevance scoring; you can swap to others like 'cross-encoder/ms-marco-electra-base'
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device=device)

def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b\w+\b", text.lower()))


def _lexical_overlap_score(query: str, chunk: str) -> float:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return 0.0
    chunk_tokens = _tokenize(chunk)
    overlap = len(query_tokens.intersection(chunk_tokens))
    return overlap / len(query_tokens)


async def retrieve_relevant_chunks(
    query: str,
    user_id: uuid.UUID,
    document_ids: Optional[List[uuid.UUID]] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_k: int = 15,
) -> List[DocumentChunk]:
    """
    Retrieve relevant chunks for a user using semantic ranking + Cross-Encoder reranking.
    """
    query_embedding = embedding_model.encode(query, convert_to_tensor=False).tolist()
    # Increased for broader initial candidates to feed into reranker
    candidate_k = max(top_k * 6, 100)

    distance_expr = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
    conditions = [Document.user_id == user_id]

    if document_ids:
        conditions.append(DocumentChunk.document_id.in_(document_ids))
    if start_date:
        conditions.append(DocumentChunk.uploaded_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        conditions.append(DocumentChunk.uploaded_at <= datetime.combine(end_date, datetime.max.time()))

    stmt = (
        select(DocumentChunk, distance_expr)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(and_(*conditions))
        .order_by(distance_expr)
        .limit(candidate_k)
    )

    async with SessionLocal() as session:
        result = await session.execute(stmt)
        rows = result.all()

    if not rows:
        logger.info("Retriever: no candidate chunks for user_id=%s", user_id)
        return []

    # Extract chunks from rows
    candidate_chunks = [chunk for chunk, distance in rows]

    # New: Use Cross-Encoder for reranking (replaces lexical + semantic hybrid)
    # This scores query-chunk pairs directly for better relevance
    pairs = [(query, chunk.content) for chunk in candidate_chunks]
    rerank_scores = cross_encoder.predict(pairs)

    # Zip and sort by rerank score (higher = more relevant)
    scored = list(zip(candidate_chunks, rerank_scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    top_scored = scored[:top_k]

    logger.info(
        "Retriever: user_id=%s candidates=%d returned=%d doc_filter=%s date_filter=%s..%s",
        user_id,
        len(rows),
        len(top_scored),
        bool(document_ids),
        start_date,
        end_date,
    )
    for idx, (chunk, score) in enumerate(top_scored[:5], start=1):
        preview = (chunk.content or "")[:120].replace("\n", " ")
        logger.debug(
            "Retriever rank=%d chunk_id=%s doc_id=%s rerank_score=%.4f preview=%s",
            idx,
            chunk.id,
            chunk.document_id,
            score,
            preview,
        )

    return [chunk for chunk, score in top_scored]
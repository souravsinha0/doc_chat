SELECT content, created_at 
FROM document_sections
WHERE document_id = :doc_id  -- Optional filter
  AND created_at >= :start_date -- Optional filter
ORDER BY embedding <=> :query_vector
LIMIT 5;
from typing import List, Dict, Optional
from qdrant_helper import search
from config import TOP_K

def retrieve_top_k_chunks(
    query_vector: List[float],
    top_k: int = TOP_K,
    file_filters: Optional[List[str]] = None
) -> List[Dict]:
    """
    Retrieve the top_k most relevant document chunks from Qdrant based on the query vector.

    Args:
        query_vector (List[float]): Embedding vector for the user query.
        top_k (int, optional): Number of top results to return.
        file_filters (List[str], optional): If set, limits results to these filenames.

    Returns:
        List[Dict]: Each dict contains chunk_id, filename, page_number, chunk_text.
    """
    print("🔍 Searching Qdrant for most relevant chunks...")

    try:
        results = search(query_vector, top_k)
        if not results:
            print("⚠️ No results found in Qdrant collection.")
            return []

        chunks = []
        for payload in results:
            if not isinstance(payload, dict):
                continue
            chunk_text = payload.get("chunk_text", "")
            filename = payload.get("filename", "")
            if file_filters is not None and filename not in file_filters:
                continue  # Skip if not in allowed files
            if not chunk_text.strip():
                continue   # Skip empty chunks
            chunks.append({
                "chunk_id": payload.get("chunk_id", ""),
                "filename": filename,
                "page_number": payload.get("page_number", ""),
                "chunk_text": chunk_text
            })

        # Uncomment for debugging
        # for i, c in enumerate(chunks):
        #     print(f"Top {i+1}: File: {c['filename']} | Page: {c['page_number']} | {c['chunk_text'][:100]}...")

        return chunks

    except Exception as e:
        print(f"❌ Qdrant search failed: {e}")
        return []


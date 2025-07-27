from typing import List, Dict, Optional
from qdrant_helper import search
from config import TOP_K

def retrieve_top_k_chunks(
    query_vector: List[float],
    top_k: int = TOP_K,
    file_filters: Optional[List[str]] = None
) -> List[Dict]:
    """
    Retrieve the top_k most relevant document chunks from Qdrant.
    """
    print("🔍 Searching Qdrant for most relevant chunks...")

    try:
        results = search(query_vector, top_k)
        if not results or not isinstance(results, list):
            print("⚠️ No results found in Qdrant collection.")
            return []

        chunks = []
        for payload in results:
            if not isinstance(payload, dict):
                continue
            chunk_text = payload.get("chunk_text", "")
            filename = payload.get("filename", "")
            page_number = payload.get("page_number", "")
            chunk_id = payload.get("chunk_id", "")

            if file_filters is not None and filename not in file_filters:
                continue
            if not isinstance(chunk_text, str) or not chunk_text.strip():
                continue

            chunks.append({
                "chunk_id": chunk_id or "",
                "filename": filename or "",
                "page_number": page_number if page_number is not None else "",
                "chunk_text": chunk_text
            })
        return chunks

    except Exception as e:
        print(f"❌ Qdrant search failed: {e}")
        return []

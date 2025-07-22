from typing import List, Dict
from qdrant_helper import search
from config import TOP_K

def retrieve_top_k_chunks(query_vector: List[float], top_k: int = TOP_K) -> List[Dict]:
    """
    Retrieve the top_k most relevant document chunks from the Qdrant collection based on query vector.

    Args:
        query_vector (List[float]): The embedding vector for the user query.
        top_k (int, optional): Number of top results to return. Defaults to TOP_K.

    Returns:
        List[Dict]: A list of dicts containing chunk_id, filename, page_number, chunk_text.
    """
    print("🔍 Searching Qdrant for most relevant chunks...")

    try:
        results = search(query_vector, top_k)

        if not results or len(results) == 0:
            print("⚠️ No results found in Qdrant collection.")
            return []

        chunks = []
        for payload in results:
            # Ensure the payload has the expected fields
            if isinstance(payload, dict):
                chunks.append({
                    "chunk_id": payload.get("chunk_id", ""),
                    "filename": payload.get("filename", ""),
                    "page_number": payload.get("page_number", ""),
                    "chunk_text": payload.get("chunk_text", "")
                })

        return chunks

    except Exception as e:
        print(f"❌ Qdrant search failed: {e}")
        return []

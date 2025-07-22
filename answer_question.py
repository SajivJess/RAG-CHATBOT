from retriever import retrieve_top_k_chunks
from embedder import embed_query
from llama_cpp_interface import generate_answer

def answer_question(user_query: str) -> dict:
    print(f"❓ User query: {user_query}")

    # Step 1: Embed the user query
    try:
        query_vector = embed_query(user_query)
    except Exception as e:
        print(f"❌ Failed to embed query: {e}")
        return {
            "answer": "Failed to process your query due to embedding error.",
            "source": None
        }

    # Step 2: Retrieve top-k relevant document chunks via Qdrant
    try:
        top_chunks = retrieve_top_k_chunks(query_vector, top_k=3)
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return {
            "answer": "Failed to retrieve relevant information.",
            "source": None
        }

    # Step 3: If no relevant chunks found, return a fallback response
    if not top_chunks:
        return {
            "answer": "No relevant context found in the documents.",
            "source": None
        }

    # Step 4: Use the most relevant chunk to generate an answer
    selected_chunk = top_chunks[0]

    if not isinstance(selected_chunk, dict) or "chunk_text" not in selected_chunk:
        return {
            "answer": "Internal error: Invalid chunk format passed to LLM.",
            "source": None
        }

    try:
        answer = generate_answer(selected_chunk, user_query)
    except Exception as e:
        print(f"❌ LLM generation failed: {e}")
        answer = "Failed to generate an answer."

    # Step 5: Return answer along with metadata
    return {
        "answer": answer,
        "source": {
            "filename": selected_chunk.get("filename", "N/A"),
            "page_number": selected_chunk.get("page_number", "N/A"),
            "chunk_id": selected_chunk.get("chunk_id", "N/A"),
            "chunk_text": selected_chunk.get("chunk_text", "")
        }
    }

from data_loader import load_documents_from_folder
from embedder import embed_and_store_chunks, embed_query
from retriever import retrieve_top_k_chunks
from llama_cpp_interface import generate_answer
from config import TOP_K
from qdrant_helper import create_collection as create_or_load_index  # Qdrant version

# Ensure Qdrant collection is loaded globally once
create_or_load_index()

def ingest_documents(folder_path: str):
    print("📥 Loading documents and preparing chunks...")
    chunks = load_documents_from_folder(folder_path)
    print(f"🧩 Total chunks generated: {len(chunks)}")
    embed_and_store_chunks(chunks)
    print("✅ Document ingestion complete.")

def answer_question(user_query: str) -> dict:
    print(f"❓ User query: {user_query}")
    # Step 1: Embed query
    try:
        query_vector = embed_query(user_query)
    except Exception as e:
        print(f"❌ Failed to embed query: {e}")
        return {
            "answer": "Failed to embed the query.",
            "source": None
        }

    # Step 2: Retrieve top-k chunks
    try:
        top_chunks = retrieve_top_k_chunks(query_vector, top_k=TOP_K)
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        return {
            "answer": "Failed to retrieve relevant context.",
            "source": None
        }

    if not top_chunks:
        return {
            "answer": "No relevant context found in the documents.",
            "source": None
        }

    selected_chunk = top_chunks[0]

    if not isinstance(selected_chunk, dict) or "chunk_text" not in selected_chunk:
        return {
            "answer": "The answer could not be generated due to invalid document format.",
            "source": None
        }

    try:
        answer = generate_answer(selected_chunk, user_query)
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        answer = "Failed to generate an answer."

    return {
        "answer": answer,
        "source": {
            "filename": selected_chunk.get("filename", "N/A"),
            "page_number": selected_chunk.get("page_number", "N/A"),
            "chunk_id": selected_chunk.get("chunk_id", "N/A"),
            "chunk_text": selected_chunk.get("chunk_text", "")
        }
    }

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) < 2:
        print("Usage:\n  python main.py ingest\n  python main.py query")
        exit()

    if sys.argv[1] == "ingest":
        folder = "documents/"
        ingest_documents(folder)

    elif sys.argv[1] == "query":
        while True:
            user_input = input("\n🔎 Ask a question (or type 'exit'): ")
            if user_input.lower() in ["exit", "quit"]:
                break

            start_time = time.time()
            result = answer_question(user_input)
            end_time = time.time()

            print(f"\n🧠 Answer: {result['answer']}")
            if result["source"]:
                print(
                    f"📄 Source: {result['source']['filename']} "
                    f"(Page {result['source']['page_number']}, Chunk {result['source']['chunk_id']})"
                )
            print(f"⚡ Response time: {end_time - start_time:.2f} sec")
    else:
        print("Unknown command. Use 'ingest' or 'query'")

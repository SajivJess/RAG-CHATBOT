import re
from retriever import retrieve_top_k_chunks
from embedder import embed_query
from llama_cpp_interface import generate_answer

def extract_relevant_lines_with_numbers(query: str, chunk_text: str, min_match=2, context_lines=0):
    """
    Returns (matched_lines:str, line_nums:List[int])
    Extracts only the most relevant line(s) plus optional lines before/after for clear proof display.
    """
    query_words = set(re.findall(r'\w+', query.lower()))
    lines = chunk_text.splitlines()
    if not lines or not any(l.strip() for l in lines):
        return "(no match)", []
    max_overlap = 0
    line_scores = []
    for i, line in enumerate(lines):
        s_words = set(re.findall(r'\w+', line.lower()))
        overlap = len(query_words & s_words)
        if overlap > max_overlap:
            max_overlap = overlap
        line_scores.append(overlap)
    found_line_nums = []
    for idx, score in enumerate(line_scores):
        if score == max_overlap and score >= min_match:
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + 1 + context_lines)
            found_line_nums.extend(i for i in range(start, end) if lines[i].strip())
    found_line_nums = sorted(set(found_line_nums))
    if found_line_nums:
        matched = " ".join([lines[i].strip() for i in found_line_nums])
        line_indices = [i+1 for i in found_line_nums]
    else:
        matched = lines[0].strip() if lines else "(no match)"
        line_indices = [1] if lines else []
    return matched, line_indices

def format_proof_context(matched_lines, page_number, line_nums):
    heading = "Proof from document:"
    if matched_lines and matched_lines.strip() and matched_lines.strip() != "(no match)":
        lines_part = f"(Located on page {page_number}, line{'s' if len(line_nums) != 1 else ''}: {line_nums})"
        return f"{heading}\n{matched_lines}\n{lines_part}"
    else:
        return f"{heading}\n(No direct supporting text was extracted from this chunk.)"

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

    # Step 5: Prepare proof-of-document context (best match lines + page + lines)
    matched_lines, matched_line_nums = extract_relevant_lines_with_numbers(
        user_query, selected_chunk.get("chunk_text", "")
    )
    proof = format_proof_context(
        matched_lines,
        selected_chunk.get("page_number", "N/A"),
        matched_line_nums
    )

    # Step 6: Return answer and proof context
    return {
        "answer": answer,
        "source": {
            "filename": selected_chunk.get("filename", "N/A"),
            "page_number": selected_chunk.get("page_number", "N/A"),
            "chunk_id": selected_chunk.get("chunk_id", "N/A"),
            "matched_content": proof
        }
    }

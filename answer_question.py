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
    found_line_nums = set()
    for idx, score in enumerate(line_scores):
        if score == max_overlap and score >= min_match:
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + 1 + context_lines)
            for i in range(start, end):
                if lines[i].strip():
                    found_line_nums.add(i)
    found_line_nums = sorted(found_line_nums)
    if found_line_nums:
        matched = " ".join([lines[i].strip() for i in found_line_nums])
        line_indices = [i + 1 for i in found_line_nums]
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

def is_list_question(user_query: str):
    """Detect if user is asking for all principles, all items, etc."""
    list_words = ["all ", "list", "principle", "principles", "bullets", "points", "enumerate"]
    t = user_query.lower()
    return any(w in t for w in list_words)

def answer_question(user_query: str) -> dict:
    print(f"❓ User query: {user_query}")

    try:
        query_vector = embed_query(user_query)
    except Exception as e:
        print(f"❌ Failed to embed query: {e}")
        return {"answer": "Failed to process your query due to embedding error.", "source": None}

    try:
        # Boost top_k to ENSURE all list chunks are fetched
        top_chunks = retrieve_top_k_chunks(query_vector, top_k=15)
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return {"answer": "Failed to retrieve relevant information.", "source": None}

    if not top_chunks or not isinstance(top_chunks[0], dict) or "chunk_text" not in top_chunks[0]:
        return {"answer": "No relevant context found in the documents.", "source": None}

    # --------- NEW: Combine all chunks that look like they have 'principle' or are list-numbered ---------
    list_chunks = []
    for c in top_chunks:
        lines = c['chunk_text'].splitlines()
        if ("principle" in c['chunk_text'].lower() 
            or sum(1 for l in lines if re.match(r'^\s*\d+\.\s', l)) > 0):
            list_chunks.append(c)
    if not list_chunks:
        list_chunks = top_chunks[:1]
    combined_text = "\n".join([c['chunk_text'] for c in list_chunks])
    selected_chunk = {
        'chunk_text': combined_text,
        'filename': list_chunks[0]['filename'],
        'page_number': list_chunks[0]['page_number'],
        'chunk_id': ",".join([c['chunk_id'] for c in list_chunks])
    }

    try:
        answer = generate_answer(selected_chunk, user_query)
    except Exception as e:
        print(f"❌ LLM generation failed: {e}")
        answer = "Failed to generate an answer."

    # Proof extraction
    matched_lines, matched_line_nums = extract_relevant_lines_with_numbers(
        user_query, selected_chunk.get("chunk_text", "")
    )
    proof = format_proof_context(
        matched_lines,
        selected_chunk.get("page_number", "N/A"),
        matched_line_nums
    )
    return {
        "answer": answer,
        "source": {
            "filename": selected_chunk.get("filename", "N/A"),
            "page_number": selected_chunk.get("page_number", "N/A"),
            "chunk_id": selected_chunk.get("chunk_id", "N/A"),
            "matched_content": proof
        }
    }

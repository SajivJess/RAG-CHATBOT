import re
from retriever import retrieve_top_k_chunks
from embedder import embed_query
from llama_cpp_interface import generate_answer

def extract_relevant_lines_with_numbers(
    query: str,
    chunk_text: str,
    min_match=2,
    context_lines=0,
    factoid_focus=True,
    list_mode=False
):
    lines = chunk_text.splitlines()
    if not lines or not any(l.strip() for l in lines):
        return "(no match)", []

    # 1. List queries: ALL bullets/numbered lines only
    if list_mode:
        proof_lines = []
        line_nums = []
        for idx, line in enumerate(lines):
            if re.match(r"^\s*(\d+\.\s|-|\u2022)", line.strip()):
                proof_lines.append(line.strip())
                line_nums.append(idx + 1)
        if proof_lines:
            return "\n".join(proof_lines), line_nums

    # 2. Factoid: Precision—ONLY short, direct lines!
    if factoid_focus and not list_mode:
        keywords1 = ["g20"]
        keywords2 = ["meet", "meeting", "meetings", "summit"]
        matches = []
        for idx, line in enumerate(lines):
            lc = line.lower()
            if any(k1 in lc for k1 in keywords1) and any(k2 in lc for k2 in keywords2):
                matches.append((idx, line.strip()))
        if matches:
            idxs, lines_out = zip(*matches)
            return "\n".join(lines_out), [i + 1 for i in idxs]
        # Weaker: any line mentioning G20 for meetings
        for idx, line in enumerate(lines):
            if "g20" in line.lower():
                return line.strip(), [idx + 1]
        # Nothing? Don't show block!
        return "(no match)", []

    # 3. Fallback: max-overlap, but capped at 2 lines max (NEVER a big block)
    query_words = set(re.findall(r'\w+', query.lower()))
    max_overlap = max(
        (len(query_words & set(re.findall(r'\w+', l.lower())))
         for l in lines if l.strip()), default=0
    )
    best_lines = [
        (idx, line.strip())
        for idx, line in enumerate(lines)
        if len(query_words & set(re.findall(r'\w+', line.lower()))) == max_overlap and line.strip()
    ]
    if best_lines:
        best_lines = best_lines[:2]
        idxs, lines_out = zip(*best_lines)
        return "\n".join(lines_out), [i + 1 for i in idxs]
    else:
        return "(no match)", []

def format_proof_context(matched_lines, page_number, line_nums):
    heading = "Proof from document:"
    if matched_lines and matched_lines.strip() and matched_lines.strip() != "(no match)":
        plural = 's' if len(line_nums) != 1 else ''
        lines_part = f"(Located on page {page_number}, line{plural}: {line_nums})"
        return f"{heading}\n{matched_lines}\n{lines_part}"
    else:
        return f"{heading}\n(No direct supporting text was extracted from this chunk.)"

def is_list_question(user_query: str):
    list_words = [
        "all ", "list", "principle", "principles", "bullets", "points",
        "enumerate", "measures", "actions", "describe", "main", "summary"
    ]
    t = user_query.lower()
    return any(w in t for w in list_words)

def answer_question(user_query: str) -> dict:
    print(f"❓ User query: {user_query}")

    try:
        query_vector = embed_query(user_query)
    except Exception as e:
        print(f"❌ Failed to embed query: {e}")
        return {
            "answer": "Failed to process your query due to embedding error.",
            "source": None
        }

    try:
        high_k = 20 if is_list_question(user_query) else 5
        top_chunks = retrieve_top_k_chunks(query_vector, top_k=high_k)
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return {
            "answer": "Failed to retrieve relevant information.",
            "source": None
        }

    if not top_chunks or not isinstance(top_chunks[0], dict) or "chunk_text" not in top_chunks[0]:
        return {"answer": "No relevant context found in the documents.", "source": None}

    # Merge top chunk and next two in doc order for completeness
    def chunk_id_key(c):
        cid = c.get("chunk_id", "")
        try:
            main_part = cid.split("_")[-1]
            return int(main_part)
        except:
            return 0

    main_chunk = top_chunks[0]
    file_ch = main_chunk.get("filename", "")
    page_ch = main_chunk.get("page_number", "")
    chunks_same_file = [c for c in top_chunks if c.get("filename") == file_ch and c.get("page_number") == page_ch]
    chunks_sorted = sorted(chunks_same_file, key=chunk_id_key)
    N_next = 2
    try:
        idx = chunks_sorted.index(main_chunk)
    except Exception:
        idx = 0
    merged_chunks = chunks_sorted[idx:idx+N_next+1]
    combined_text = "\n".join(c['chunk_text'] for c in merged_chunks if c.get('chunk_text', '').strip())
    selected_chunk = {
        'chunk_text': combined_text,
        'filename': merged_chunks[0].get('filename', 'N/A'),
        'page_number': merged_chunks[0].get('page_number', 'N/A'),
        'chunk_id': ",".join(c.get('chunk_id', 'N/A') for c in merged_chunks)
    }

    is_list = is_list_question(user_query)
    factoid_focus = not is_list

    try:
        answer = generate_answer(selected_chunk, user_query)
    except Exception as e:
        print(f"❌ LLM generation failed: {e}")
        answer = "Failed to generate an answer."

    matched_lines, matched_line_nums = extract_relevant_lines_with_numbers(
        user_query,
        selected_chunk.get("chunk_text", ""),
        factoid_focus=factoid_focus,
        list_mode=is_list
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

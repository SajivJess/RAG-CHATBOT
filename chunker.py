import os
import re

SECTION_HEADER_PAT = re.compile(r"^[A-Z][A-Za-z0-9 ,\-\(\)/]+: ?$")  # e.g. "Scope of Work:", "Requirements:", etc.

def chunk_text(text: str, max_tokens: int = 400, overlap: int = 50):
    """
    Improved chunker: keeps section headings with their content if present,
    otherwise performs sentence-based overlap chunking.
    """
    # 1. Split into logical blocks: group lines under a section header
    lines = text.strip().split('\n')
    blocks = []
    current_block = []
    for line in lines:
        if SECTION_HEADER_PAT.match(line.strip()):
            if current_block:
                blocks.append("\n".join(current_block).strip())
                current_block = []
            current_block = [line.strip()]  # start new block with header
        else:
            current_block.append(line.strip())
    if current_block:
        blocks.append("\n".join(current_block).strip())

    # 2. Now, for each block, chunk by sentences with overlap if block is long
    chunks = []
    for block in blocks:
        sentences = re.split(r'(?<=[.!?])\s+', block)
        current_chunk = []
        current_len = 0
        for sentence in sentences:
            sentence_len = len(sentence.split())
            if current_len + sentence_len > max_tokens and current_chunk:
                chunk_text_str = " ".join(current_chunk).strip()
                if chunk_text_str and len(chunk_text_str.split()) >= 10:
                    chunks.append(chunk_text_str)
                # Add overlap (in tokens, not sentences)
                flat_tokens = " ".join(current_chunk).split()
                overlap_tokens = flat_tokens[-overlap:] if overlap > 0 else []
                current_chunk = [" ".join(overlap_tokens)] if overlap_tokens else []
                current_len = len(overlap_tokens)
            current_chunk.append(sentence)
            current_len += sentence_len
        # Add leftover
        final_chunk = " ".join(current_chunk).strip()
        if final_chunk and len(final_chunk.split()) >= 10:
            chunks.append(final_chunk)
    return chunks

def process_pdf(file_path):
    import fitz
    doc = fitz.open(file_path)
    all_chunks = []
    fname = os.path.basename(file_path)
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        for i, chunk in enumerate(chunk_text(text)):
            if chunk.strip() and len(chunk.split()) >= 10:
                all_chunks.append({
                    "filename": fname,
                    "page_number": page_num + 1,
                    "chunk_id": f"{page_num+1}_{i}",
                    "chunk_text": chunk
                })
    return all_chunks

def process_docx(file_path):
    import docx
    fname = os.path.basename(file_path)
    doc = docx.Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)
    results = []
    for i, chunk in enumerate(chunk_text(text)):
        if chunk.strip() and len(chunk.split()) >= 10:
            results.append({
                "filename": fname,
                "page_number": 0,
                "chunk_id": f"docx_0_{i}",
                "chunk_text": chunk
            })
    return results

def process_documents(paths):
    all_chunks = []
    for path in paths:
        lower = path.lower()
        if lower.endswith(".pdf"):
            all_chunks.extend(process_pdf(path))
        elif lower.endswith(".docx"):
            all_chunks.extend(process_docx(path))
    return all_chunks

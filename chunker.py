import os
import re

SECTION_HEADER_PAT = re.compile(r"^[A-Z][A-Za-z0-9 ,\-\(\)/]+: ?$")

def chunk_text(text: str):
    """
    Yields each section from its header to the next header as a single chunk (no mid-section splitting).
    """
    lines = [l.strip() for l in text.strip().split('\n')]
    blocks = []
    current_block = []
    for line in lines:
        if not line: continue
        if SECTION_HEADER_PAT.match(line):
            if current_block and sum(len(w.split()) for w in current_block) >= 10:
                blocks.append("\n".join(current_block))
            current_block = [line]
        else:
            current_block.append(line)
    if current_block and sum(len(w.split()) for w in current_block) >= 10:
        blocks.append("\n".join(current_block))
    return blocks

def process_pdf(file_path):
    import fitz
    doc = fitz.open(file_path)
    all_chunks = []
    fname = os.path.basename(file_path)
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        for i, chunk in enumerate(chunk_text(text)):
            if len(chunk.split()) >= 10:
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
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)
    results = []
    for i, chunk in enumerate(chunk_text(text)):
        if len(chunk.split()) >= 10:
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

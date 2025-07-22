# chunker.py
# Recursive sentence-based splitter with overlap
# Metadata includes: filename, page_number, chunk_id, chunk_text

def chunk_text(text: str, max_tokens: int = 400, overlap: int = 50):
    import re
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    current_chunk = []
    current_len = 0
    for sentence in sentences:
        sentence_len = len(sentence.split())
        if current_len + sentence_len > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-(overlap // 10):]  # approx
            current_len = sum(len(s.split()) for s in current_chunk)
        current_chunk.append(sentence)
        current_len += sentence_len
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def process_pdf(file_path):
    import fitz
    doc = fitz.open(file_path)
    all_chunks = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "filename": file_path.split("/")[-1],
                "page_number": page_num + 1,
                "chunk_id": f"{page_num+1}_{i}",
                "chunk_text": chunk
            })
    return all_chunks

def process_docx(file_path):
    import docx
    doc = docx.Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip() != ""]
    text = "\n".join(paragraphs)
    chunks = chunk_text(text)
    return [{
        "filename": file_path.split("/")[-1],
        "page_number": 0,
        "chunk_id": f"docx_0_{i}",
        "chunk_text": chunk
    } for i, chunk in enumerate(chunks)]

def process_documents(paths):
    all_chunks = []
    for path in paths:
        if path.endswith(".pdf"):
            all_chunks.extend(process_pdf(path))
        elif path.endswith(".docx"):
            all_chunks.extend(process_docx(path))
    return all_chunks

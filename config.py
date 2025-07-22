# === Chunking Settings ===
CHUNK_MAX_TOKENS = 250              # Maximum tokens per chunk
CHUNK_OVERLAP_TOKENS = 50           # Overlap tokens between chunks
CHUNK_ENCODING = 'utf-8'            # Fallback encoding

# === Embedding Model Config ===
EMBEDDING_MODEL_NAME = "intfloat/e5-small-v2"  # HuggingFace model or local path
EMBEDDING_DIMENSION = 384                     # Must match the embedding model

# === Vector Store (Qdrant, replaces FAISS) ===
QDRANT_COLLECTION = "docs"
QDRANT_PATH = "./qdrant_data"
TOP_K = 3                                      # Number of chunks to retrieve

# (Optional/backup:)  # === FAISS (Unused with Qdrant, keep for reference)
# FAISS_INDEX_PATH = "vector_store/faiss_index.bin"
# VECTOR_METADATA_PATH = "vector_store/vector_metadata.json"

# === LLM Config ===
LLM_MODE = "llama.cpp"                         # Use llama.cpp for local GGUF models
LLM_MODEL_PATH = "models/llama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
LLM_MAX_INPUT_TOKENS = 1024
DEVICE = "cpu"                                 # or "gpu" if using CUDA-enabled llama.cpp build

PROMPT_TEMPLATE = """
[Instruction]: Using only the content below, return the most concise and specific answer to the user's question.
If possible, quote or summarize just the most relevant sentence, clause, or bullet from the provided content.

If the answer is not present, reply: "The answer is not available in the provided documents."
Document Source:
File: {filename}
Page: {page_number}
Chunk ID: {chunk_id}
{chunk_text}
User Question: {user_query}
"""

# === UI Settings ===
UI_TITLE = "🦙 Offline RAG Chatbot"
UI_DESCRIPTION = "Upload documents and ask questions. Answers come ONLY from your files."
UI_THEME = "dark"                               # Options: "dark" or "light"

# === Performance Settings ===
RESPONSE_TIME_WARNING_THRESHOLD = 15            # Warn if response takes too long (in seconds)

# === Logging & Debug ===
LOG_LATENCY = True
LOG_DIR = "logs/"
SAVE_RESPONSES = True

# === File Support ===
SUPPORTED_EXTENSIONS = [".pdf", ".docx"]


# === Chunker Functions ===
# Recursive sentence-based splitter with overlap
# Metadata includes: filename, page_number, chunk_id, chunk_text

def chunk_text(text: str, max_tokens: int = CHUNK_MAX_TOKENS, overlap: int = CHUNK_OVERLAP_TOKENS):
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

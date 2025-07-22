import os
import fitz  # PyMuPDF
import uuid
from embedder import embed_and_store_chunks
from qdrant_helper import create_collection as create_or_load_index  # Qdrant!

# === CONFIG ===
CHUNK_SIZE = 300       # Number of words per chunk
CHUNK_OVERLAP = 50     # Number of overlapping words between chunks
DOCS_DIR = "documents"

def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks of specified word size."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def load_and_chunk_pdf(pdf_path):
    """Load a single PDF and return its split text chunks."""
    doc = fitz.open(pdf_path)
    filename = os.path.basename(pdf_path)
    all_chunks = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()
        for chunk in split_text(text):
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "filename": filename,
                "page_number": page_number,
                "chunk_text": chunk
            })

    return all_chunks

def process_all_pdfs():
    """Iterate over all PDF files in the docs folder and chunk them."""
    print("📚 Loading PDFs from 'docs/'...")
    all_chunks = []
    for fname in os.listdir(DOCS_DIR):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(DOCS_DIR, fname)
            chunks = load_and_chunk_pdf(path)
            print(f"📄 {fname}: {len(chunks)} chunks")
            all_chunks.extend(chunks)
    return all_chunks

if __name__ == "__main__":
    create_or_load_index()  # Qdrant: ensure collection exists before storage
    chunks = process_all_pdfs()
    embed_and_store_chunks(chunks)  # Stores to Qdrant

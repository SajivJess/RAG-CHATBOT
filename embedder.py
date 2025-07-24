from typing import List, Dict
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer('intfloat/e5-small-v2', device='cuda')
# or, after instantiation:
# embedder = embedder.to('cuda')

from qdrant_helper import create_collection, add_documents, search
from config import EMBEDDING_MODEL_NAME

import uuid
import json
import os

# Load embedding model once
print("🔤 Loading embedding model...")
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Paths for storing offline backup metadata (optional, for data transparency)
METADATA_FILE = "vector_metadata.json"

def embed_and_store_chunks(chunks: List[Dict]):
    vectors = []
    metadata = []

    for chunk in chunks:
        embedding = embedder.encode(chunk['chunk_text']).tolist()
        vectors.append(embedding)
        metadata.append({
            "id": str(uuid.uuid4()),
            "filename": chunk["filename"],
            "page_number": chunk["page_number"],
            "chunk_id": chunk["chunk_id"],
            "chunk_text": chunk["chunk_text"]
        })

    print(f"📤 Adding {len(vectors)} vectors to Qdrant collection...")
    add_documents(vectors, metadata)

    # Save (optional) metadata alongside index
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("✅ Qdrant and metadata saved offline.")

def embed_query(query: str) -> List[float]:
    return embedder.encode(query).tolist()

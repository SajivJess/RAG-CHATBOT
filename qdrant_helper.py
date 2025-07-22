from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import numpy as np
from config import QDRANT_COLLECTION, QDRANT_PATH, EMBEDDING_DIMENSION

client = QdrantClient(path=QDRANT_PATH)  # Stores data locally (offline mode!)

def create_collection():
    """
    Ensure the Qdrant collection exists.
    """
    existing = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE)
        )

def add_documents(vectors, payloads):
    """
    Add vectors and payloads (metadata) to Qdrant collection.
    """
    create_collection()
    existing_count = client.count(QDRANT_COLLECTION).count or 0
    points = [
        PointStruct(id=existing_count + i, vector=np.array(v, dtype=np.float32), payload=p)
        for i, (v, p) in enumerate(zip(vectors, payloads))
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)

def search(query_vector, top_k=3):
    """
    Search for top_k most similar vectors and return their payloads.
    """
    create_collection()
    res = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=np.array(query_vector, dtype=np.float32),
        limit=top_k
    )
    return [hit.payload for hit in res]

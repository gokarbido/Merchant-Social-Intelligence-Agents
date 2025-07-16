import numpy as np
from typing import List

# Placeholder: Replace with real embedding model (e.g., Ollama, OpenAI, etc.)
def get_embedding(text: str) -> np.ndarray:
    # For demo, use a hash-based pseudo-embedding
    np.random.seed(abs(hash(text)) % (2**32))
    return np.random.rand(384)

# FAISS integration
import faiss

class FaissIndex:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.vectors = []
        self.texts = []
    def add(self, text: str):
        emb = get_embedding(text).astype('float32')
        self.index.add(emb.reshape(1, -1))
        self.vectors.append(emb)
        self.texts.append(text)
    def search(self, query: str, k=5) -> List[str]:
        emb = get_embedding(query).astype('float32').reshape(1, -1)
        D, I = self.index.search(emb, k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)]

# ChromaDB integration (optional, for persistent search)
import chromadb
from chromadb.config import Settings

class ChromaDBIndex:
    def __init__(self, collection_name="agents", persist_directory=".chromadb"):
        self.client = chromadb.Client(Settings(persist_directory=persist_directory))
        self.collection = self.client.get_or_create_collection(collection_name)
    def add(self, text: str):
        emb = get_embedding(text).tolist()
        self.collection.add(documents=[text], embeddings=[emb], ids=[str(hash(text))])
    def search(self, query: str, k=5) -> List[str]:
        emb = get_embedding(query).tolist()
        results = self.collection.query(query_embeddings=[emb], n_results=k)
        return results['documents'][0] if results['documents'] else [] 
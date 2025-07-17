import numpy as np
from typing import List

from agents.ollama_client import OllamaClient

# Simple embedding function (replace with real model in production)
ollama_client = OllamaClient()

def get_embedding(text: str) -> np.ndarray:
    return np.array(ollama_client.embed(text))

# FAISS integration
import faiss

class FaissIndex:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.vectors = []
        self.ids = []  # Store merchant_ids
    def add(self, merchant_id: str, text: str):
        emb = get_embedding(text).astype('float32')
        self.index.add(emb.reshape(1, -1))
        self.vectors.append(emb)
        self.ids.append(merchant_id)
    def search(self, query: str, k=5) -> List[str]:
        emb = get_embedding(query).astype('float32').reshape(1, -1)
        D, I = self.index.search(emb, k)
        return [self.ids[i] for i in I[0] if i < len(self.ids)]

# ChromaDB integration
import chromadb
from chromadb.config import Settings

class ChromaDBIndex:
    def __init__(self, collection_name="agents", persist_directory=".chromadb"):
        self.client = chromadb.Client(Settings(persist_directory=persist_directory))
        self.collection = self.client.get_or_create_collection(collection_name)
    def add(self, merchant_id: str, text: str):
        emb = get_embedding(text).tolist()
        self.collection.add(documents=[text], embeddings=[emb], ids=[merchant_id])
    def search(self, query: str, k=5) -> List[str]:
        emb = get_embedding(query).tolist()
        results = self.collection.query(query_embeddings=[emb], n_results=k)
        return results['ids'][0] if results['ids'] else [] 
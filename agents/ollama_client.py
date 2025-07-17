import requests
import os

OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

class OllamaClient:
    def __init__(self, model=DEFAULT_MODEL):
        self.model = model
        self.embedding_model = os.environ.get("OLLAMA_EMBEDDING_MODEL", "all-minilm")

    def generate(self, prompt: str) -> str:
        response = requests.post(
            OLLAMA_URL,
            json={"model": self.model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"].strip()

    def embed(self, text: str):
        url = OLLAMA_URL.replace("/api/generate", "/api/embeddings")
        response = requests.post(
            url,
            json={"model": self.embedding_model, "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"] 
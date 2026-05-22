import os
import httpx
from app.core.config import settings
from typing import List

class EmbeddingClient:
    def __init__(self):
        self.embed_url = f"{settings.OLLAMA_URL}/api/embeddings"
        self.model = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")

    async def generate_embedding(self, text: str) -> List[float]:
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.embed_url, json=payload, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("embedding", [])
            else:
                raise Exception(f"Failed to generate embedding: {response.text}")

embedding_client = EmbeddingClient()

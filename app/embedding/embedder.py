import os
from typing import List
from openai import OpenAI
from app.core.config import settings

class Embedder:
    """
    Handles text embedding generation using OpenAI's API.
    This is memory-efficient and perfect for free-tier deployments.
    """
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small" # 1536 dimensions
        self._cache = {}

    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a single string using OpenAI."""
        if not text:
            return []
            
        # Check cache to save money/time
        if text in self._cache:
            return self._cache[text]
            
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            embedding = response.data[0].embedding
            
            # Simple LRU cache management
            if len(self._cache) > 1000:
                self._cache.clear()
            self._cache[text] = embedding
            
            return embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of strings."""
        if not texts:
            return []
            
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return [[0.0] * 1536 for _ in texts]

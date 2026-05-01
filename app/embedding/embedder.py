from typing import List
from sentence_transformers import SentenceTransformer

class Embedder:
    """
    Handles generation of vector embeddings from text chunks using SentenceTransformers.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        # Load the model locally (downloads on first run)
        self.model = SentenceTransformer(self.model_name)
        # In-memory LRU cache for single text embeddings (max 1000 unique queries)
        self._embed_cache: dict = {}

    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a single piece of text, with caching."""
        if text in self._embed_cache:
            return self._embed_cache[text]
        
        embedding = self.model.encode(text).tolist()
        
        # Evict oldest entry if cache is full
        if len(self._embed_cache) >= 1000:
            oldest_key = next(iter(self._embed_cache))
            del self._embed_cache[oldest_key]
        
        self._embed_cache[text] = embedding
        return embedding

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts with batch_size optimization."""
        if not texts:
            return []
        embeddings = self.model.encode(texts, batch_size=32)
        return embeddings.tolist()

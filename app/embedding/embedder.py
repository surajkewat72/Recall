from typing import List

class Embedder:
    """
    Handles generation of vector embeddings from text chunks.
    """
    
    def __init__(self, model_name: str = "text-embedding-ada-002"):
        self.model_name = model_name
        # Initialize embedding model client (e.g., OpenAI, HuggingFace) here

    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a single piece of text."""
        pass

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        pass

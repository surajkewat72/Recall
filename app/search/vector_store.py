import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

class VectorStore:
    """
    Handles interactions with the ChromaDB vector database.
    This version runs locally without Docker!
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.index_name = "rag_chunks"
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.index_name,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )

    def get_file_modified_time(self, doc_id: str) -> Optional[str]:
        """Get the modified time of an existing document from the index."""
        results = self.collection.get(
            where={"doc_id": doc_id},
            include=["metadatas"],
            limit=1
        )
        if results and results['metadatas']:
            return results['metadatas'][0].get("modified_time")
        return None

    def delete_document(self, doc_id: str):
        """Delete all chunks associated with a specific document ID."""
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(f"Warning: Could not delete document chunks for {doc_id}. {e}")

    def index_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Store document chunks and their embeddings in ChromaDB."""
        if not chunks or not embeddings or len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must be non-empty and of equal length.")
            
        ids = [f"{chunk.get('doc_id')}_{i}" for i, chunk in enumerate(chunks)]
        documents = [chunk.get("chunk_text", "") for chunk in chunks]
        metadatas = [
            {
                "doc_id": chunk.get("doc_id", ""),
                "file_name": chunk.get("file_name", ""),
                "source": chunk.get("source", "gdrive"),
                "modified_time": chunk.get("modified_time", "")
            }
            for chunk in chunks
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 5, file_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search ChromaDB for similar embeddings with optional filtering."""
        
        where_filter = None
        if file_name:
            where_filter = {"file_name": file_name}
            
        response = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        # Format results to match the previous structure
        results = []
        if response and response['documents']:
            for doc, meta in zip(response['documents'][0], response['metadatas'][0]):
                results.append({
                    "chunk_text": doc,
                    "file_name": meta.get("file_name"),
                    "source": meta.get("source")
                })
        return results

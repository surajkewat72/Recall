import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import re
from groq import Groq
from cachetools import TTLCache

from app.core.config import settings
from app.connectors.gdrive import GoogleDriveConnector
from app.processing.document import DocumentProcessor
from app.embedding.embedder import Embedder
from app.search.vector_store import VectorStore

api_router = APIRouter()

# Initialize Singletons for the router
processor = DocumentProcessor()
embedder = Embedder()
vector_store = VectorStore()
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

# RAG Result Cache: Max 500 items, expires in 3600 seconds (1 hour)
rag_cache = TTLCache(maxsize=500, ttl=3600)

class SyncRequest(BaseModel):
    url: Optional[str] = None

class SyncDriveResponse(BaseModel):
    file_id: str
    file_name: str
    mime_type: str
    chunks_indexed: int

class AskRequest(BaseModel):
    query: str
    file_name: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    sources: List[str]

@api_router.get("/status")
async def api_status():
    """Simple API status check."""
    return {"status": "operational", "groq_configured": groq_client is not None}

@api_router.post("/sync-drive", response_model=List[SyncDriveResponse])
async def sync_drive(request: Optional[SyncRequest] = None):
    """
    Sync files from Google Drive asynchronously in parallel.
    Optionally sync a specific file by URL.
    """
    credentials_file = settings.GDRIVE_CREDENTIALS_FILE
    token_file = settings.GDRIVE_TOKEN_FILE
    
    connector = GoogleDriveConnector(
        credentials_file=credentials_file,
        token_file=token_file
    )
    
    try:
        await asyncio.to_thread(connector.authenticate)
        
        url_file_id = None
        if request and request.url:
            match = re.search(r'/d/([a-zA-Z0-9_-]+)', request.url)
            if match:
                url_file_id = match.group(1)
            elif "id=" in request.url:
                match = re.search(r'id=([a-zA-Z0-9_-]+)', request.url)
                if match:
                    url_file_id = match.group(1)
            
            if not url_file_id:
                raise HTTPException(status_code=400, detail="Could not extract File ID from Google Drive URL.")
                
        if url_file_id:
            def fetch_single_file():
                return connector.service.files().get(
                    fileId=url_file_id, 
                    fields="id, name, mimeType, modifiedTime"
                ).execute()
                
            try:
                file_data = await asyncio.to_thread(fetch_single_file)
                files = [file_data]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Could not access the specific file. Ensure you have permissions. {e}")
        else:
            files = await asyncio.to_thread(connector.list_files)
        
        async def process_single_file(file):
            file_id = file.get('id')
            file_name = file.get('name')
            mime_type = file.get('mimeType')
            modified_time = file.get('modifiedTime')
            
            # Incremental sync check
            existing_modified_time = await asyncio.to_thread(vector_store.get_file_modified_time, file_id)
            if existing_modified_time and existing_modified_time == modified_time:
                print(f"Skipping {file_name}, already up to date.")
                return None
                
            # If it exists but is updated, delete old chunks first
            if existing_modified_time:
                print(f"Updating {file_name}, deleting old chunks.")
                await asyncio.to_thread(vector_store.delete_document, file_id)
            
            try:
                # 1. Download
                file_path = await asyncio.to_thread(
                    connector.download_file,
                    file_id=file_id, 
                    file_name=file_name, 
                    mime_type=mime_type
                )
                
                # 2. Process and Chunk
                with open(file_path, "rb") as f:
                    content = f.read()
                    
                actual_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if mime_type == "application/vnd.google-apps.document" else mime_type
                
                chunks = await asyncio.to_thread(processor.process, content, actual_mime, file_id, file_name, modified_time)
                
                # 3. Embed and Index
                if chunks:
                    texts = [chunk["chunk_text"] for chunk in chunks]
                    embeddings = await asyncio.to_thread(embedder.embed_texts, texts)
                    await asyncio.to_thread(vector_store.index_chunks, chunks, embeddings)
                
                return SyncDriveResponse(
                    file_id=file_id,
                    file_name=file_name,
                    mime_type=mime_type,
                    chunks_indexed=len(chunks)
                )
                
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
                return None
                
        # Gather all tasks to run concurrently
        tasks = [process_single_file(file) for file in files]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results (skipped or errored files)
        return [r for r in results if r is not None]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Drive sync failed: {str(e)}")

@api_router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    RAG endpoint: Converts query to embedding, searches vector store,
    and uses Groq LLM to generate an answer grounded in the sources.
    """
    if not groq_client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured.")
        
    query = request.query
    
    # Check cache
    cache_key = f"{query}_{request.file_name}"
    if cache_key in rag_cache:
        return rag_cache[cache_key]
    
    # 1. Embed query
    query_embedding = await asyncio.to_thread(embedder.embed_text, query)
    
    # 2. Search vector store
    results = await asyncio.to_thread(vector_store.search, query_embedding, top_k=5, file_name=request.file_name)
    
    if not results:
        return AskResponse(answer="I couldn't find any relevant information in the documents.", sources=[])
        
    # 3. Build context and sources
    context_texts = []
    sources_set = set()
    
    for hit in results:
        context_texts.append(hit.get("chunk_text", ""))
        sources_set.add(hit.get("file_name", "Unknown"))
        
    context_block = "\n\n---\n\n".join(context_texts)
    
    # 4. Generate answer with Groq
    system_prompt = "You must answer only using the provided context"
    
    user_prompt = f"Context:\n{context_block}\n\nQuestion: {query}"
    
    try:
        chat_completion = await asyncio.to_thread(
            groq_client.chat.completions.create,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="llama-3.3-70b-versatile", # Updated to a supported high-performance model
            temperature=0.2,
        )
        
        answer = chat_completion.choices[0].message.content
        response = AskResponse(answer=answer, sources=list(sources_set))
        rag_cache[cache_key] = response
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation failed: {str(e)}")

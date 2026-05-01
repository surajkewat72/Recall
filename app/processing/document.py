import io
import re
from typing import List, Dict, Any
from pdfminer.high_level import extract_text
import docx

class DocumentProcessor:
    """
    Handles parsing and chunking of documents fetched from external sources.
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def parse_file(self, content: bytes, mime_type: str) -> str:
        """
        Parse raw bytes from a given file based on its mime type.
        Extracts clean text, removes empty lines, and normalizes whitespace.
        """
        text = ""
        
        if mime_type == "application/pdf":
            text = self._parse_pdf(content)
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = self._parse_docx(content)
        elif mime_type == "text/plain":
            text = content.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported mime type: {mime_type}")
            
        return self._clean_text(text)

    def _parse_pdf(self, content: bytes) -> str:
        """Extract text from a PDF."""
        file_stream = io.BytesIO(content)
        return extract_text(file_stream)

    def _parse_docx(self, content: bytes) -> str:
        """Extract text from a DOCX file."""
        file_stream = io.BytesIO(content)
        doc = docx.Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs])
        
    def _clean_text(self, text: str) -> str:
        """
        Clean the extracted text:
        - Remove empty lines
        - Normalize whitespace
        """
        lines = text.splitlines()
        clean_lines = []
        for line in lines:
            # Normalize whitespace: replace multiple spaces with single space
            line = re.sub(r'\s+', ' ', line).strip()
            if line: # If line is not empty
                clean_lines.append(line)
                
        return "\n".join(clean_lines)

    def chunk_text(self, text: str, doc_id: str, file_name: str, modified_time: str) -> List[Dict[str, Any]]:
        """Split parsed text into word-based chunks with metadata mapping."""
        chunks = []
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return chunks
            
        start = 0
        chunk_index = 0
        
        while start < total_words:
            end = min(start + self.chunk_size, total_words)
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "chunk_text": chunk_text,
                "doc_id": doc_id,
                "file_name": file_name,
                "source": "gdrive",
                "chunk_index": chunk_index,
                "modified_time": modified_time
            })
            
            # If we've reached the end, break out
            if end >= total_words:
                break
                
            start += self.chunk_size - self.chunk_overlap
            chunk_index += 1
            
        return chunks
        
    def process(self, content: bytes, mime_type: str, doc_id: str, file_name: str, modified_time: str) -> List[Dict[str, Any]]:
        """Parse and chunk a document from raw bytes, returning structured metadata."""
        text = self.parse_file(content, mime_type)
        return self.chunk_text(text, doc_id, file_name, modified_time)

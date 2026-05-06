import json
import numpy as np
import google.generativeai as genai
from typing import List, Tuple
from app.config import config

class EmbeddingManager:
    """Manages text chunking and embedding generation using Gemini"""
    
    def __init__(self):
        """Initialize embedding model"""
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
            
        return chunks if chunks else [text]  # Return original if too small
    
    def load_and_chunk_data(self, content_file: str) -> Tuple[List[str], List[dict]]:
        """Load JSON data and create text chunks"""
        with open(content_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = []
        metadatas = []
        
        print(f"Loading {len(data['pages'])} pages from content...")
        
        for page in data['pages']:
            # Create rich text with title context
            text = f"Title: {page['title']}\n\nContent: {page['content']}"
            
            # Split into chunks
            text_chunks = self.chunk_text(text)
            
            for chunk in text_chunks:
                chunks.append(chunk)
                metadatas.append({
                    "title": page['title'],
                    "source": page['title']
                })
        
        print(f"Created {len(chunks)} chunks from content")
        return chunks, metadatas
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text using Gemini API"""
        try:
            # Truncate text if too long (embedding models have limits)
            if len(text) > 2000:
                text = text[:2000]
                
            result = genai.embed_content(
                model=config.EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error getting embedding for text: {text[:100]}...")
            print(f"Error details: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        embeddings = []
        total = len(texts)
        
        for i, text in enumerate(texts):
            print(f"  Generating embedding {i+1}/{total}")
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
            
        return embeddings
# backend/app/embedding.py
import json
import google.generativeai as genai
from typing import List, Tuple
from app.config import config
from app.pdf_processor import PDFProcessor
import os

class EmbeddingManager:
    """Manages text chunking and embedding generation"""
    
    def __init__(self):
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.pdf_processor = PDFProcessor()
        
    def chunk_text(self, text: str, chunk_size: int = 800) -> List[str]:
        """Simple text chunking"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks if chunks else [text[:chunk_size]]
    
    def load_and_chunk_data(self, content_file: str = None) -> Tuple[List[str], List[dict]]:
        """Load data from PDFs first, fallback to JSON"""
        chunks = []
        metadatas = []
        
        # Try to load from PDFs first
        print("\n📚 Loading e-commerce data from PDFs...")
        pdf_chunks = self.pdf_processor.process_all_pdfs()
        
        if pdf_chunks:
            for item in pdf_chunks:
                chunks.append(item['text'])
                metadatas.append(item['metadata'])
            print(f"\n✅ Loaded {len(chunks)} chunks from PDF files")
        else:
            # Fallback to JSON if no PDFs found
            print("⚠️ No PDFs found, using JSON fallback...")
            if content_file and os.path.exists(content_file):
                with open(content_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for page in data.get('pages', []):
                    text = f"Topic: {page['title']}\n{page['content']}"
                    text_chunks = self.chunk_text(text)
                    
                    for chunk in text_chunks:
                        chunks.append(chunk)
                        metadatas.append({"source": page['title'], "type": "json"})
                
                print(f"✅ Loaded {len(chunks)} chunks from JSON")
        
        return chunks, metadatas
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini"""
        try:
            if len(text) > 2000:
                text = text[:2000]
                
            result = genai.embed_content(
                model=config.EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0.0] * 768
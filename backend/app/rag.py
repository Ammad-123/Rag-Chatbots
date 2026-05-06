import numpy as np
import google.generativeai as genai
from typing import List, Tuple
from app.config import config
from app.embedding import EmbeddingManager
import os
import pickle
import asyncio

class SimpleVectorStore:
    """Simple vector store using numpy and cosine similarity"""
    
    def __init__(self):
        self.chunks = []
        self.metadatas = []
        self.embeddings = []
        self.embedding_manager = EmbeddingManager()
    
    def add_texts(self, texts: List[str], metadatas: List[dict]):
        """Add texts to vector store"""
        self.chunks = texts
        self.metadatas = metadatas
        
        print(f"Generating {len(texts)} embeddings...")
        for i, text in enumerate(texts):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(texts)}")
            embedding = self.embedding_manager.get_embedding(text)
            self.embeddings.append(embedding)
        
        print(f"✓ Ready with {len(self.chunks)} chunks")
    
    def similarity_search(self, query: str, k: int = 3) -> List[Tuple[str, dict, float]]:
        """Search for similar content"""
        query_embedding = self.embedding_manager.get_embedding(query)
        
        similarities = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(emb) + 1e-8)
            similarities.append(sim)
        
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.2:
                results.append((self.chunks[idx], self.metadatas[idx], similarities[idx]))
        
        return results
    
    def save(self, path: str):
        """Save to disk"""
        with open(path, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'metadatas': self.metadatas,
                'embeddings': self.embeddings
            }, f)
    
    def load(self, path: str) -> bool:
        """Load from disk"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.metadatas = data['metadatas']
                self.embeddings = data['embeddings']
            return True
        return False

class RAGSystem:
    """Lightweight website support chatbot"""
    
    def __init__(self):
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.vector_store = SimpleVectorStore()
        self.embedding_manager = EmbeddingManager()
        self.model = genai.GenerativeModel(config.LLM_MODEL)
        self._setup()
    
    def _setup(self):
        """Initialize vector store"""
        os.makedirs(config.PERSIST_DIR, exist_ok=True)
        store_path = os.path.join(config.PERSIST_DIR, "vectors.pkl")
        
        if self.vector_store.load(store_path):
            print(f"✓ Loaded {len(self.vector_store.chunks)} chunks from cache")
        else:
            print("📚 Creating new vector store...")
            chunks, metas = self.vector_store.embedding_manager.load_and_chunk_data(config.CONTENT_FILE)
            self.vector_store.add_texts(chunks, metas)
            self.vector_store.save(store_path)
            print(f"✓ Created store with {len(chunks)} chunks")
    
    async def stream_answer(self, question: str, websocket=None, client_id=None):
        """Stream answer as lightweight support chatbot"""
        try:
            # Send start event
            if websocket and client_id:
                await websocket.send_json({
                    'type': 'start',
                    'message': '🔍 Looking up...'
                })
            
            # Search for relevant content
            results = self.vector_store.similarity_search(question, k=config.TOP_K_RESULTS)
            
            if not results:
                if websocket and client_id:
                    await websocket.send_json({
                        'type': 'complete',
                        'content': "I don't have that information."
                    })
                return
            
            # Send context message
            if websocket and client_id:
                await websocket.send_json({
                    'type': 'context',
                    'message': ''
                })
            
            # Prepare context
            context = "\n\n".join([chunk for chunk, _, _ in results])
            
            # Lightweight support chatbot prompt
            prompt = f"""You are a lightweight website support chatbot.

RULES:
- Keep answers short (max 5-7 lines)
- Use simple everyday English
- Avoid marketing or sales language
- Do NOT introduce yourself every time
- Do NOT repeat the company name unless necessary
- Use bullet points only if helpful
- If user asks a question, answer directly
- If information is missing, say: "I don't have that information."

TONE: Friendly, helpful, concise, natural.

FORMAT: Prefer short paragraphs, avoid long explanations

CONTEXT: {context}

USER QUESTION: {question}

ANSWER:"""
            
            # Stream from Gemini
            response = self.model.generate_content(prompt, stream=True)
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    
                    if websocket and client_id:
                        await websocket.send_json({
                            'type': 'chunk',
                            'content': chunk.text
                        })
                    
                    await asyncio.sleep(0.01)
            
            # Send completion
            if websocket and client_id:
                await websocket.send_json({
                    'type': 'complete',
                    'full_response': full_response.strip()
                })
            
        except Exception as e:
            error_msg = str(e)
            print(f"Streaming error: {error_msg}")
            
            if websocket and client_id:
                await websocket.send_json({
                    'type': 'error',
                    'content': "Sorry, I'm having trouble. Please try again."
                })
    
    def get_answer(self, question: str) -> str:
        """Get non-streaming answer as lightweight support chatbot"""
        try:
            results = self.vector_store.similarity_search(question, k=config.TOP_K_RESULTS)
            
            if not results:
                return "I don't have that information."
            
            context = "\n\n".join([chunk for chunk, _, _ in results])
            
            prompt = f"""You are a lightweight website support chatbot.

RULES:
- Keep answers short (max 5-7 lines)
- Use simple everyday English
- Avoid marketing or sales language
- Do NOT introduce yourself every time
- Do NOT repeat the company name unless necessary
- Use bullet points only if helpful
- Answer directly
- If missing info, say: "I don't have that information."

TONE: Friendly, helpful, concise

CONTEXT: {context}

QUESTION: {question}

ANSWER:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            if "429" in str(e):
                return "Service is busy. Please wait a moment."
            return "Sorry, I'm having trouble. Please try again."
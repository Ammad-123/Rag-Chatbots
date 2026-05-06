import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # Google Gemini API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # CORRECT model names based on available models
    # Lightweight + working embedding model
    EMBEDDING_MODEL = "models/gemini-embedding-001"
    
    # FASTEST + cheapest chat model (best for chatbot)
    LLM_MODEL = "models/gemini-flash-lite-latest"
    
    # RAG settings
    CHUNK_SIZE = 1000 
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 3
    
    # Data file
    CONTENT_FILE = "app/data/content.json"
    
    # Vector store
    PERSIST_DIR = "./chroma_db"

config = Config()
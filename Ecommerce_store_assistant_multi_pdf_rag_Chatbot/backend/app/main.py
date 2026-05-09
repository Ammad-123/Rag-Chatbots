from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from app.rag import RAGSystem

# Initialize FastAPI App
app = FastAPI(title="Stable AI Chatbot", version="3.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the RAG System
print("Initializing RAG System...")
rag = RAGSystem()
print("RAG System Ready!")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
async def health():
    return {"status": "online", "mode": "HTTP"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Standard HTTP POST endpoint for chat.
    Reliable, stateless, and simple.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    print(f"Received request: {request.message[:50]}...")
    
    try:
        # Get the full answer from the RAG system
        result = await rag.get_answer_async(request.message)
        print(f"AI Response: {result['content']}")
        return result
    except Exception as e:
        print(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

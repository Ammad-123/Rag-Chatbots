from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import uuid
from app.rag import RAGSystem
import asyncio

app = FastAPI(title="AI Chatbot", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "ws://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Initialize RAG
print("Starting AI Chatbot with WebSocket Streaming...")
rag = RAGSystem()
print("Ready!")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat")
async def chat(request: ChatRequest):
    """REST endpoint for non-streaming chat"""
    if not request.message:
        raise HTTPException(400, "Empty message")
    
    answer = rag.get_answer(request.message)
    return ChatResponse(answer=answer)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """WebSocket endpoint for real-time streaming"""
    await websocket.accept()
    
    if not client_id:
        client_id = str(uuid.uuid4())
    
    print(f"Client {client_id} connected")
    
    try:
        # Send welcome message
        await websocket.send_json({
            'type': 'connected',
            'message': 'Connected to AI Assistant',
            'client_id': client_id
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            question = message_data.get('message', '')
            
            if question:
                print(f"Received question from {client_id}: {question[:50]}...")
                # Stream the answer - FIXED: properly await the async function
                await rag.stream_answer(question, websocket, client_id)
    
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"Error in websocket endpoint: {e}")
        try:
            await websocket.send_json({
                'type': 'error',
                'content': f"Server error: {str(e)}"
            })
        except:
            pass

@app.get("/health")
async def health():
    return {"status": "healthy", "model": "gemini-2.0-flash", "websocket": True}

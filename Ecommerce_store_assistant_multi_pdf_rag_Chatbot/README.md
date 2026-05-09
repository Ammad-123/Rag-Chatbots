# AI Chatbot System with Google Gemini & RAG

A complete end-to-end AI chatbot system with Retrieval Augmented Generation (RAG) using Google Gemini, LangChain, FastAPI, and React.

## Features

- 🤖 **AI-Powered Responses**: Uses Google Gemini Pro for intelligent answers
- 📚 **RAG System**: Retrieves relevant information from website content
- 💬 **Real-time Chat**: Clean, modern chat widget interface
- ⚡ **Streaming Support**: Optional streaming responses for real-time interaction
- 🐳 **Dockerized**: Easy deployment with Docker Compose
- 🎨 **Modern UI**: Floating chat widget with smooth animations

## Prerequisites

- Docker and Docker Compose
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

## Quick Start

1. **Clone the repository**
```bash
git clone <your-repo>
cd ai-chatbot



# Backend
cp backend/.env.example backend/.env
# Edit backend/.env and add your GOOGLE_API_KEY

# Or use docker-compose environment
export GOOGLE_API_KEY="your_api_key_here"



docker-compose up --build


Access the application

Frontend: http://localhost:5173

Backend API: http://localhost:8000

API Docs: http://localhost:8000/docs



cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
uvicorn app.main:app --reload --port 8000



Frontend Setup
bash
cd frontend
npm install
npm run dev



ai-chatbot/
├── backend/          # FastAPI backend with RAG
│   ├── app/
│   │   ├── main.py   # API endpoints
│   │   ├── rag.py    # RAG implementation
│   │   ├── embedding.py # Embedding management
│   │   └── data/     # Sample content
├── frontend/         # React frontend
│   └── src/
│       └── components/ # Chat UI components
└── docker-compose.yml


Testing the API
Curl Request (Non-streaming)
bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How much does AI Assistant Pro cost?"}'
Expected Response
json
{
  "answer": "AI Assistant Pro costs $49 per month for the basic plan and $99 per month for the pro plan. Enterprise pricing is available upon request."
}
Streaming Endpoint
bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your products"}'
Sample Questions to Ask
"How much does AI Assistant Pro cost?"

"What are your pricing plans?"

"How do I get support?"

"Can I integrate with Slack?"

"What security measures do you have?"

"Do you provide training?"

Project Structure


How It Works
Content Ingestion: Website content is loaded from content.json, split into chunks, and converted to embeddings using Google's embedding model.




uv pip install -r requirements.txt
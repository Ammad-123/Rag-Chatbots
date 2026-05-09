import asyncio
import os
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv

# =========================
# CONFIGURATION & LOGGING
# =========================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in .env file.")
    raise ValueError("GEMINI_API_KEY not found in .env. Please add it to continue.")

# =========================
# AI MODEL SETUP
# =========================
genai.configure(api_key=GEMINI_API_KEY)

# Using Gemini 1.5 Flash for optimal speed and cost-efficiency
MODEL_NAME = "gemini-2.5-flash-lite" 
model = genai.GenerativeModel(model_name=MODEL_NAME)

# =========================
# API INITIALIZATION
# =========================
app = FastAPI(
    title="🚀 Multi-Prompt Automation API",
    description="High-performance API to process multiple AI prompts in parallel.",
    version="1.1.0",
    contact={
        "name": "Support",
        "url": "https://www.etsy.com/shop/CodeWithHafizAmmad",
    }
)

# =========================
# SCHEMAS
# =========================
class PromptRequest(BaseModel):
    prompts: List[str] = Field(..., example=["Write a poem", "Explain gravity", "Top 5 travel spots"])

class PromptResponse(BaseModel):
    prompt: str
    response: str

# =========================
# CORE LOGIC
# =========================
async def generate_ai_response(prompt: str) -> Dict[str, str]:
    """
    Generates a response from Gemini for a given prompt.
    Wrapped in asyncio.to_thread to prevent blocking the event loop.
    """
    try:
        logger.info(f"Processing prompt: {prompt[:50]}...")
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        return {
            "prompt": prompt,
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}")
        return {
            "prompt": prompt,
            "response": f"⚠️ ERROR: {str(e)}"
        }

# =========================
# ENDPOINTS
# =========================
@app.post("/generate", response_model=Dict[str, Any])
async def generate_multiple_prompts(request: PromptRequest):
    """
    ### Handle Multiple Prompts in Parallel
    This endpoint takes a list of prompts and processes them simultaneously using Gemini.
    """
    if not request.prompts:
        raise HTTPException(
            status_code=400,
            detail="Prompts list cannot be empty"
        )

    logger.info(f"Received {len(request.prompts)} prompts for processing.")
    
    # Create parallel tasks
    tasks = [generate_ai_response(p) for p in request.prompts]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)

    return {
        "status": "success",
        "total_prompts": len(request.prompts),
        "results": results
    }

@app.get("/", tags=["Health Check"])
async def root():
    """Welcome endpoint with service information."""
    return {
        "message": "Welcome to the Multi-Prompt Automation API",
        "model": MODEL_NAME,
        "docs": "/docs",
        "status": "active"
    }

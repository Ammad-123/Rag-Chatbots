# 🚀 Multi-Prompt Automation API (Gemini-Powered)

Elevate your productivity with this high-performance, asynchronous API designed to handle multiple AI prompts simultaneously. Built with **FastAPI** and powered by **Google Gemini**, this tool is perfect for developers, researchers, and content creators who need to process large volumes of prompts efficiently.

---

## ✨ Key Features

- **⚡ Parallel Processing**: Processes multiple prompts at once using Python's `asyncio`, significantly reducing wait times.
- **🤖 Gemini Integration**: Utilizes the latest Gemini models (Gemini Flash Lite) for fast and cost-effective responses.
- **🛠️ Production Ready**: Built with FastAPI, including automatic Swagger UI documentation and robust error handling.
- **🔌 Easy Integration**: Simple JSON API interface that can be called from any language (Python, JS, C#, etc.).
- **🔒 Secure**: Environment variable support for API keys.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **AI Model**: Google Gemini 2.5 Flash Lite
- **Runtime**: Python 3.9+
- **Concurrency**: Asyncio

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have Python installed. You can download it from [python.org](https://www.python.org/).

### 2. Installation
Clone or extract the files, then install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration
1. Rename `.env.example` to `.env`.
2. Get your Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
3. Add your key to the `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

### 4. Running the API
Start the server using Uvicorn:
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

---

## 📖 Usage Example

### Endpoint: `POST /generate`

Send a JSON request with a list of prompts:

**Request Body:**
```json
{
  "prompts": [
    "Write a short poem about coding.",
    "Explain the concept of Quantum Computing in 2 sentences.",
    "Generate a list of 5 healthy breakfast ideas."
  ]
}
```

**Response:**
```json
{
  "total_prompts": 3,
  "results": [
    {
      "prompt": "Write a short poem about coding.",
      "response": "Lines of logic, neat and clean..."
    },
    ...
  ]
}
```

---

## 🎨 Interactive Documentation
Once the server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the Etsy Community.**

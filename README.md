<div align="center">

```
   █████╗ ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗
  ██╔══██╗██║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
  ███████║██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
  ██╔══██║██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
  ██║  ██║██████╗██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
  ╚═╝  ╚═╝╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
```

### Multi-Modal AI Assistant
**Analysis • Vision • Web Browsing**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

**By Pratik Raj**

[Features](#features) • [Installation](#installation) • [API Docs](#api-endpoints) • [Screenshots](#screenshots)

</div>

---

## Overview

A powerful multi-modal AI assistant combining advanced language models with vision analysis and web browsing. Toggle between online, cloud, and local AI models for comprehensive intelligent assistance.(still incomplete  , agentic features not added yet )

```
┌──────────────────┬────────────────────────────────────┐
│  TEXT CHAT       │  Conversational AI with PDF context│
│  VISION          │  Image understanding & analysis    │
│  WEB BROWSING    │  Automated scraping & screenshots  │
└──────────────────┴────────────────────────────────────┘
```

---

## Features

- **Text Analysis** - Chat powered by GPT-OSS, DeepSeek, Nemotron models
- **Vision Analysis** - Moondream 1.8B (local) and Molmo 2 8B (online)
- **Web Browsing** - Playwright-powered scraping with screenshots
- **Model Toggle** - Switch between Online/Cloud/Local models seamlessly
- **PDF Context** - Upload documents for context-aware responses
- **Local Storage** - Persistent conversation history in JSON format
- **Modern UI** - Dark theme with neon green accents and Orbitron font

---

## Tech Stack

<table>
<tr><td><b>Backend</b></td><td>FastAPI (Python)</td></tr>
<tr><td><b>Frontend</b></td><td>Streamlit</td></tr>
<tr><td><b>AI (Online)</b></td><td>OpenRouter API (Nemotron, Qwen, Molmo)</td></tr>
<tr><td><b>AI (Cloud)</b></td><td>Ollama Cloud (GPT-OSS, DeepSeek, Qwen3-Coder)</td></tr>
<tr><td><b>AI (Local)</b></td><td>Ollama (LLaVA, Moondream, TinyLlama)</td></tr>
<tr><td><b>Vision</b></td><td>Moondream 1.8B, Molmo 2 8B</td></tr>
<tr><td><b>Storage</b></td><td>Local JSON (rag_storage.json)</td></tr>
<tr><td><b>Web Scraping</b></td><td>Playwright (Headless Chrome)</td></tr>
</table>

---

## Installation

```bash
# Clone repository
git clone https://github.com/PRATIK-4751/Agent.git
cd Agent

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure environment variables
cp .env.example .env
# Add your API keys to .env

# Start backend server
python -m uvicorn server:app --host 127.0.0.1 --port 8002

# Start frontend (new terminal)
python -m streamlit run streamlit_app.py

# Open browser at http://localhost:8501
```

---

## Project Structure

```
Agent/
├── server.py           # FastAPI backend with 3 endpoints
├── streamlit_app.py    # Streamlit frontend UI
├── text.py             # Text response handler
├── vision.py           # Vision/image analysis
├── browsing.py         # Web browser automation
├── rag_storage.py      # Local JSON storage manager
├── pratik_prompt.py    # System prompt configuration
├── requirements.txt    # Python dependencies
├── .env                # API keys (not in repo)
└── rag_storage.json    # Local conversation storage
```

---

## API Endpoints

```
┌────────────────────┬────────┬──────────────────────────┐
│  Endpoint          │ Method │ Description              │
├────────────────────┼────────┼──────────────────────────┤
│  /text-analyze     │  POST  │ Text chat with context   │
│  /vision-analyze   │  POST  │ Image analysis           │
│  /browse           │  POST  │ Web browsing + Q&A       │
│  /health           │  GET   │ Health check             │
└────────────────────┴────────┴──────────────────────────┘
```

### Example: Text Analysis

```json
POST /text-analyze
{
  "text": "Your question here",
  "context": "Optional PDF context",
  "use_online": true
}

Response:
{
  "response": "AI generated response",
  "model_used": "nemotron-70b-instruct",
  "timestamp": "2024-01-13T10:30:00Z"
}
```

### Example: Vision Analysis

```json
POST /vision-analyze
{
  "image": "base64_encoded_image",
  "question": "What's in this image?",
  "use_online": true
}

Response:
{
  "analysis": "Detailed image description",
  "elements": ["mountains", "boats", "sunset"],
  "model_used": "moondream:1.8b"
}
```

### Example: Web Browse

```json
POST /browse
{
  "url": "https://example.com",
  "question": "Summarize this page",
  "use_online": true
}

Response:
{
  "content": "Page content extracted",
  "screenshot": "base64_image",
  "answer": "AI analysis of the page"
}
```

---

## Screenshots

### Landing Page - Main Interface

<div align="center">
  <img src="https://raw.githubusercontent.com/PRATIK-4751/Agent/master/Assests/image.png" alt="AI Agent Landing Page" width="800"/>
  
  *Clean dark-themed interface with mode selection, PDF upload, model toggle (Online/Local), and text input area*
</div>

---

### Vision Analysis - Input Image

<div align="center">
  <img src="https://raw.githubusercontent.com/PRATIK-4751/Agent/master/Assests/picture.jpg" alt="Vision Input - Landscape" width="800"/>
  
  *Example input: Japanese-inspired landscape with dramatic sunset, mountains, boats, and stylized waves*
</div>

---

### Vision Analysis - AI Output

<div align="center">
  <img src="https://raw.githubusercontent.com/PRATIK-4751/Agent/master/Assests/image%20copy.png" alt="Vision Analysis Output" width="800"/>
  
  *Detailed AI-generated analysis with element breakdown: mountains, sky reflections, boats, and atmospheric description*
</div>

---

## Configuration

Create a `.env` file in the project root:

```bash
# OpenRouter API (Required for Online Models)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Ollama Cloud (Optional - for Cloud Models)
OLLAMA_CLOUD_URL=https://ollama.com
OLLAMA_CLOUD_API_KEY=your-ollama-cloud-key

# API Configuration
API_BASE_URL=http://127.0.0.1:8002

# Application Settings
APP_HOST=127.0.0.1
APP_PORT=8002
DEBUG_MODE=false
```

---

## Model Fallback Chain

The system automatically falls back to alternative models if primary models fail:

```
┌─────────────────────┐
│  Request Received   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Ollama Cloud       │
│  (Primary)          │
│  DeepSeek, Qwen     │
└──────────┬──────────┘
           │ Failed?
           ▼
┌─────────────────────┐
│  OpenRouter API     │
│  (Secondary)        │
│  Nemotron, Molmo    │
└──────────┬──────────┘
           │ Failed?
           ▼
┌─────────────────────┐
│  Local Ollama       │
│  (Fallback)         │
│  Moondream, LLaVA   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Return Response    │
└─────────────────────┘
```

---

## Usage

### Text Mode
- Enter your question in the text area
- Optionally upload a PDF for context
- Toggle Online/Local model
- Click "Send >>" to get AI response

### Vision Mode
- Upload an image (JPG, PNG, etc.)
- Ask questions about the image
- Get detailed visual analysis with element breakdown

### Browse Mode
- Enter a URL to scrape
- AI will extract content and take a screenshot
- Ask questions about the webpage
- Get intelligent analysis of the content

---

## Key Features Explained

### System Prompt Integration
The AI identifies as "Pratik AI Agent" and maintains consistent personality across all interactions.

### RAG Storage
Conversations are automatically stored in `rag_storage.json` for context-aware responses across sessions.

### PDF Context Support
Upload PDFs in Text mode to provide additional context for more accurate and relevant responses.

### Screenshot Capture
Web browsing mode automatically captures screenshots for visual reference and analysis.

---

## Contributing

Contributions are welcome! Here's how you can help:

```bash
# 1. Fork the repository
# 2. Create your feature branch
git checkout -b feature/AmazingFeature

# 3. Commit your changes
git commit -m 'Add some AmazingFeature'

# 4. Push to the branch
git push origin feature/AmazingFeature

# 5. Open a Pull Request
```

### Contribution Guidelines
- Follow PEP 8 style guide for Python code
- Add comments for complex logic
- Update documentation for new features
- Test your changes thoroughly

---


<div align="center">



</div>

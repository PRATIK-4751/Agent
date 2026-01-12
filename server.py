from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field, BaseModel
import asyncio
from browsing import WebBrowser
from text import TextResponseHandler
from rag_storage import rag_storage, get_rag_context, add_conversation_to_rag
import json
import os

# Create FastAPI app with a specific route for static files
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request models
class BrowseRequest(BaseModel):
    url: str = Field(..., description="URL to browse")
    query: str = Field(..., description="User's question about the page")

class TextRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt to analyze")
    use_local: bool = Field(default=True, description="Whether to use local model")
    context: list = Field(default=[], description="Chat context/history for RAG")
    pdf_content: str = Field(default=None, description="PDF content to use as context")

class VisionRequest(BaseModel):
    image_data: str = Field(..., description="Base64 encoded image data")
    prompt: str = Field(..., description="Prompt for vision analysis")
    use_local: bool = Field(default=True, description="Whether to use local model")
    context: list = Field(default=[], description="Chat context/history for RAG")

# API endpoint for browsing
@app.post("/browse")
async def browse_web(request: BrowseRequest):
    browser = WebBrowser()
    try:
        result = await browser.capture_and_process(request.url, request.query)
        return result
    except Exception as e:
        error_detail = {
            "error": str(e),
            "url": request.url,
            "query": request.query
        }
        raise HTTPException(status_code=500, detail=error_detail)
    finally:
        await browser.close_browser()


@app.post("/text-analyze")
async def text_analyze(request: TextRequest):
    try:
        handler = TextResponseHandler()
        
        
        # First, get any relevant context from RAG storage based on the current prompt
        rag_context = get_rag_context(request.prompt)
        
        # Build the full prompt with various context sources
        context_parts = []
        
        # Add RAG retrieved context if available
        if rag_context:
            context_parts.append(f"Relevant Information from Knowledge Base:\n{rag_context}")
        
        # Add PDF content as context if provided
        if request.pdf_content:
            context_parts.append(f"PDF Content:\n{request.pdf_content}")
        
        # Add conversation history as context
        if request.context:
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.context])
            context_parts.append(f"Previous conversation:\n{context_str}")
        
        # Combine all context parts
        if context_parts:
            combined_context = "\n\n".join(context_parts)
            full_prompt = f"Context:\n{combined_context}\n\nUser: {request.prompt}"
        else:
            full_prompt = request.prompt
            
        response = handler.get_response(full_prompt, use_local=request.use_local)
        
        # Store the conversation in RAG storage for future retrieval
        if request.context and len(request.context) > 0:
            # Add the last few exchanges to RAG for context
            for msg in request.context[-2:]:  # Store last 2 exchanges
                if msg['role'] == 'user':
                    # We'll add this when we have the AI response
                    continue
        
        # Add the current exchange to RAG storage
        last_user_msg = request.prompt
        ai_response = response
        add_conversation_to_rag(last_user_msg, ai_response)
        
        return {
            "response": response,
            "prompt": request.prompt,
            "model_used": "local" if request.use_local else "online"
        }
    except Exception as e:
        error_detail = {
            "error": str(e),
            "prompt": request.prompt
        }
        raise HTTPException(status_code=500, detail=error_detail)

# API endpoint for vision analysis
@app.post("/vision-analyze")
async def vision_analyze(request: VisionRequest):
    try:
        # Import here to avoid circular imports
        from vision import vision_to_text
        import tempfile
        import base64
        
        # Decode the base64 image data
        image_bytes = base64.b64decode(request.image_data)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_bytes)
            temp_image_path = temp_file.name
        
        # Build context-aware prompt if context is provided
        if request.context:
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.context])
            full_prompt = f"Context:\n{context_str}\n\nUser: {request.prompt}"
        else:
            full_prompt = request.prompt
        
        # Perform vision analysis
        result = vision_to_text(
            temp_image_path, 
            full_prompt, 
            vision_local=request.use_local, 
            text_local=request.use_local
        )
        
        # Clean up the temporary file
        import os
        os.unlink(temp_image_path)
        
        return {
            "response": result,
            "prompt": request.prompt,
            "model_used": "local" if request.use_local else "online"
        }
    except Exception as e:
        error_detail = {
            "error": str(e),
            "prompt": request.prompt
        }
        raise HTTPException(status_code=500, detail=error_detail)

# Serve the main page
@app.get("/")
async def root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "browser-api"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
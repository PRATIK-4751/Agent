from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field, BaseModel
from browsing import WebBrowser
from text import TextResponseHandler
from supabase_rag import get_rag_context, add_conversation_to_rag
import base64
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BrowseRequest(BaseModel):
    url: str = Field(..., description="URL to browse")
    query: str = Field(..., description="User's question about the page")

class TextRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt to analyze")
    use_local: bool = Field(default=False, description="Whether to use local model")
    context: list = Field(default=[], description="Chat context/history")
    pdf_content: str = Field(default=None, description="PDF content as context")

class VisionRequest(BaseModel):
    image_data: str = Field(..., description="Base64 encoded image data")
    prompt: str = Field(..., description="Prompt for vision analysis")
    use_local: bool = Field(default=False, description="Whether to use local model")
    context: list = Field(default=[], description="Chat context/history")

@app.post("/browse")
async def browse_web(request: BrowseRequest):
    browser = WebBrowser()
    try:
        result = await browser.capture_and_process(request.url, request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "url": request.url})
    finally:
        await browser.close_browser()

@app.post("/text-analyze")
async def text_analyze(request: TextRequest):
    try:
        handler = TextResponseHandler()
        rag_context = get_rag_context(request.prompt)
        context_parts = []
        
        if rag_context:
            context_parts.append(f"Relevant Information from Knowledge Base:\n{rag_context}")
        if request.pdf_content:
            context_parts.append(f"PDF Content:\n{request.pdf_content}")
        if request.context:
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.context])
            context_parts.append(f"Previous conversation:\n{context_str}")
        
        if context_parts:
            full_prompt = f"Context:\n{chr(10).join(context_parts)}\n\nUser: {request.prompt}"
        else:
            full_prompt = request.prompt
            
        response = handler.get_response(full_prompt, use_local=request.use_local)
        add_conversation_to_rag(request.prompt, response)
        
        return {
            "response": response,
            "prompt": request.prompt,
            "model_used": "local" if request.use_local else "online"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "prompt": request.prompt})

@app.post("/vision-analyze")
async def vision_analyze(request: VisionRequest):
    try:
        from vision import vision_to_text
        
        image_bytes = base64.b64decode(request.image_data)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_bytes)
            temp_image_path = temp_file.name
        
        if request.context:
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.context])
            full_prompt = f"Context:\n{context_str}\n\nUser: {request.prompt}"
        else:
            full_prompt = request.prompt
        
        result = vision_to_text(temp_image_path, full_prompt, vision_local=request.use_local, text_local=request.use_local)
        os.unlink(temp_image_path)
        
        return {
            "response": result,
            "prompt": request.prompt,
            "model_used": "local" if request.use_local else "online"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "prompt": request.prompt})

@app.get("/")
async def root():
    return {"status": "ok", "service": "AI Agent API", "endpoints": ["/browse", "/text-analyze", "/vision-analyze"]}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "browser-api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
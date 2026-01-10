from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os
from datetime import datetime
import uuid

from app import ask
from browser import search_web
from memory import retrieve_memories, store_memory, count_memories
from decider import memory_decider
from session import save_message, get_session_history

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = "You are a helpful AI assistant with long-term memory. You have access to web search functionality. When users ask you to search for information, provide details from the search results included in the prompt. Be concise and cite sources when referencing search results. If search results are provided, use them to enhance your answers but also share the source information with the user."
PROVIDER = "local"

@app.post("/chat")
async def chat(
    message: str = Form(...),
    session_id: str = Form(...),
    image: UploadFile | None = None
):
    image_path = None

    if image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(await image.read())
            image_path = f.name

    conversation_history = get_session_history(session_id, limit=6)

    query_context = message
    if conversation_history:
        recent = " ".join([msg['content'] for msg in conversation_history[-4:]])
        query_context = f"{recent} {message}"

    memories = retrieve_memories(query_context, top_k=5)
    
    filtered_memories = []
    seen_content = set()
    
    for m in memories:
        if m.get('similarity', 0) < 0.6:
            continue
        
        content_lower = m['content'].lower()
        if content_lower not in seen_content:
            filtered_memories.append(m)
            seen_content.add(content_lower)

    # Build memory context
    memory_context = ""
    if filtered_memories:
        lines = ["[Relevant context from your memory]:"]
        for i, m in enumerate(filtered_memories[:3], 1):
            lines.append(f"{i}. {m['content']}")
        memory_context = "\n".join(lines) + "\n\n"

    final_prompt = memory_context + message

    response = ask(
        PROVIDER,
        SYSTEM_PROMPT,
        final_prompt,
        image_path=image_path
    )

    save_message(session_id, "user", message, image_path)
    save_message(session_id, "assistant", response)

    decision = memory_decider(
        ask,
        PROVIDER,
        SYSTEM_PROMPT,
        message,
        response,
        image_included=image_path is not None,
        conversation_history=[(msg['role'], msg['content']) for msg in conversation_history[-6:]]
    )

    memory_stored = None
    if decision:
        store_memory(
            content=decision["content"],
            mem_type=decision["mem_type"],
            importance=decision["importance"],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "has_image": image_path is not None,
                "session_id": session_id
            }
        )
        memory_stored = decision["content"]

    if image_path:
        os.remove(image_path)

    return {
        "response": str(response),
        "memories_used": [m['content'] for m in filtered_memories[:3]],
        "memory_stored": memory_stored
    }

@app.get("/memory-count")
async def get_memory_count():
    count = count_memories()
    return {"count": count}

@app.get("/session/{session_id}/history")
async def get_history(session_id: str):
    history = get_session_history(session_id)
    return {"history": history}

@app.post("/web-search")
async def web_search(query: str = Form(...)):
    try:
        search_results = search_web(query, max_results=5)
        
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "title": result["title"],
                "url": result["url"],
                "snippet": result["snippet"]
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    except Exception as e:
        return {"error": str(e), "results": [], "count": 0}
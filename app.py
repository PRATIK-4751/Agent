import requests
import base64
import os
from memory import retrieve_memories, store_memory
from decider import memory_decider
from dotenv import load_dotenv
from browser import search_web

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava:7b"

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def ask_ollama(system_prompt, user_prompt, image_path=None):
    memories = retrieve_memories(user_prompt, top_k=3)
    memory_context = ""
    if memories:
        memory_context = "\n\n[Previous context from memory]:\n"
        for m in memories:
            memory_context += f"- {m['content']}\n"
    
    full_prompt = memory_context + "\n" + user_prompt

    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": full_prompt,
        "stream": False
    }

    if image_path:
        payload["images"] = [encode_image(image_path)]

    res = requests.post(OLLAMA_URL, json=payload)
    if res.status_code != 200:
        raise Exception(res.text)
    return res.json()["response"]

def ask_openrouter(system_prompt, user_prompt, image_path=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Vision-Agent"
    }

    memories = retrieve_memories(user_prompt, top_k=3)
    
    messages = [{"role": "system", "content": system_prompt}]
    
    
    if memories:
        memory_text = "[Previous context from your memory]:\n"
        for m in memories:
            memory_text += f"- {m['content']}\n"
        messages.append({"role": "system", "content": memory_text})

    content = [{"type": "text", "text": user_prompt}]

    if image_path:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
            }
        })

    messages.append({"role": "user", "content": content})

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages
    }

    res = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    if res.status_code != 200:
        raise Exception(res.text)
    return res.json()["choices"][0]["message"]["content"]

def ask(provider, system_prompt, user_prompt, image_path=None):
    # Check if user wants to perform a web search
    if "search " in user_prompt.lower() or "web search" in user_prompt.lower() or "look up " in user_prompt.lower():
        # Extract search query from prompt
        search_terms = ["search for ", "search ", "web search for ", "look up ", "find "]
        query = user_prompt
        
        for term in search_terms:
            if term in user_prompt.lower():
                start_idx = user_prompt.lower().find(term) + len(term)
                query = user_prompt[start_idx:].strip()
                break
        
        # Perform web search
        search_results = search_web(query, max_results=5)
        
        if search_results:
            search_summary = "Here are the search results:\n\n"
            for i, result in enumerate(search_results[:3]):  # Limit to top 3 results
                search_summary += f"Result {i+1}:\n"
                search_summary += f"Title: {result['title']}\n"
                search_summary += f"URL: {result['url']}\n"
                search_summary += f"Snippet: {result['snippet']}\n\n"
            
            # Append search results to the user prompt
            enhanced_prompt = f"{user_prompt}\n\nWeb Search Results:\n{search_summary}"
        else:
            enhanced_prompt = f"{user_prompt}\n\nI tried searching the web for information, but couldn't find relevant results."
    else:
        enhanced_prompt = user_prompt
    
    if provider == "local":
        reply = ask_ollama(system_prompt, enhanced_prompt, image_path)
    elif provider == "online":
        reply = ask_openrouter(system_prompt, enhanced_prompt, image_path)
    else:
        raise Exception("Invalid provider")

    return reply
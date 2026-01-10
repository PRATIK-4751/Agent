import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

MEMORY_ENDPOINT = f"{SUPABASE_URL}/rest/v1/memories"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

_embedding_cache = {}

def embed_text(text: str) -> List[float]:
    if text in _embedding_cache:
        return _embedding_cache[text]
    
    payload = {
        "model": "nomic-embed-text:latest",
        "prompt": text
    }
    r = requests.post(OLLAMA_EMBED_URL, json=payload)
    if r.status_code != 200:
        raise Exception(r.text)
    
    embedding = r.json()["embedding"]
    _embedding_cache[text] = embedding
    
    if len(_embedding_cache) > 100:
        _embedding_cache.pop(next(iter(_embedding_cache)))
    
    return embedding

def store_memory(
    content: str, 
    mem_type: str = "chat_summary", 
    source: str = "conversation", 
    importance: int = 1,
    metadata: Dict[str, Any] = None
) -> bool:
    embedding = embed_text(content)

    payload = {
        "content": content,
        "type": mem_type,
        "source": source,
        "importance": importance,
        "embedding": embedding,
        "metadata": metadata or {}
    }

    r = requests.post(MEMORY_ENDPOINT, headers=HEADERS, json=payload)
    if r.status_code not in [200, 201]:
        raise Exception(r.text)
    return True

def retrieve_memories(query: str, top_k: int = 5, min_similarity: float = 0.5) -> List[Dict]:
    embedding = embed_text(query)

    payload = {
        "query_embedding": embedding,
        "match_count": top_k * 2,
        "match_threshold": min_similarity
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/match_memories",
        headers=HEADERS,
        json=payload
    )
    
    if r.status_code != 200:
        raise Exception(r.text)
    
    results = r.json()
    
    
    for item in results:
        importance_boost = item.get('importance', 1) * 0.1
        item['final_score'] = item.get('similarity', 0) + importance_boost
    
    results.sort(key=lambda x: x['final_score'], reverse=True)
    
    return results[:top_k]

def count_memories() -> int:
    r = requests.get(
        f"{MEMORY_ENDPOINT}?select=count",
        headers={**HEADERS, "Prefer": "count=exact"}
    )
    if r.status_code == 200:
        count_header = r.headers.get('Content-Range', '')
        if '/' in count_header:
            return int(count_header.split('/')[-1])
    return 0
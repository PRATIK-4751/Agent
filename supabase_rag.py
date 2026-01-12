import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

class SupabaseRAGStorage:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
        if not url or not key or not SUPABASE_AVAILABLE:
            raise ValueError("Supabase not configured")
        self.supabase: Client = create_client(url, key)
        self.table_name = "rag_context"
    
    def add_context(self, content: str, source_type: str = "general", metadata: Dict = None) -> str:
        try:
            response = self.supabase.table(self.table_name).insert({
                "content": content,
                "source_type": source_type,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat()
            }).execute()
            return response.data[0]["id"]
        except Exception as e:
            return _add_local_context(content, source_type, metadata)
    
    def search_context(self, query: str, top_k: int = 5) -> List[Dict]:
        try:
            response = self.supabase.table(self.table_name).select("*").order("created_at", desc=True).limit(top_k).execute()
            return response.data
        except Exception:
            return _search_local_context(query, top_k)

def _add_local_context(content: str, source_type: str = "general", metadata: Dict = None) -> str:
    storage_file = "rag_storage.json"
    data = []
    
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = []
    
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    entry = {
        "id": content_hash,
        "content": content,
        "source_type": source_type,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat()
    }
    
    exists = False
    for i, existing in enumerate(data):
        if existing["id"] == content_hash:
            data[i] = entry
            exists = True
            break
    
    if not exists:
        data.append(entry)
    
    try:
        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return content_hash
    except:
        return ""

def _search_local_context(query: str, top_k: int = 5) -> List[Dict]:
    storage_file = "rag_storage.json"
    if not os.path.exists(storage_file):
        return []
    
    try:
        with open(storage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        query_words = query.lower().split()
        scored = []
        
        for entry in data:
            content_lower = entry["content"].lower()
            score = sum(1 for word in query_words if word in content_lower)
            if score > 0:
                scored.append((entry, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, score in scored[:top_k]]
    except:
        return []

try:
    supabase_rag = SupabaseRAGStorage()
except:
    supabase_rag = None

def get_rag_context(query: str = "") -> str:
    if not supabase_rag:
        storage_file = "rag_storage.json"
        if not os.path.exists(storage_file):
            return ""
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not data:
                return ""
            return "\n".join([entry["content"] for entry in data[-5:]])
        except:
            return ""
    
    relevant = supabase_rag.search_context(query) if query else supabase_rag.search_context("", top_k=5)
    if not relevant:
        return ""
    
    return "\n".join([f"--- Context ---\n{entry.get('content', '')}\n---------------" for entry in relevant])

def add_conversation_to_rag(user_message: str, ai_response: str, session_id: str = None) -> str:
    content = f"User: {user_message}\nAI: {ai_response}"
    metadata = {"session_id": session_id, "type": "conversation", "user_message": user_message, "ai_response": ai_response}
    
    if supabase_rag:
        return supabase_rag.add_context(content, "conversation", metadata)
    return _add_local_context(content, "conversation", metadata)
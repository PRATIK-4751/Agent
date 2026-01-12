import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client

class SupabaseRAGStorage:
    """
    RAG storage system using Supabase for persistent storage
    """
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(url, key)
        self.table_name = "rag_context"
    
    def add_context(self, content: str, source_type: str = "general", metadata: Dict = None) -> str:
        """Add content as context to the RAG storage"""
        if not metadata:
            metadata = {}
        
        try:
            response = self.supabase.table(self.table_name).insert({
                "content": content,
                "source_type": source_type,
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            return response.data[0]["id"]
        except Exception as e:
            print(f"Error adding context to Supabase: {e}")
            # Fallback to local storage
            return self._add_local_context(content, source_type, metadata)
    
    def _add_local_context(self, content: str, source_type: str = "general", metadata: Dict = None) -> str:
        """Fallback to local storage if Supabase fails"""
        # Implement fallback to local JSON storage
        storage_file = "rag_storage.json"
        data = []
        
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []
        
        # Create a simple ID based on content
        import hashlib
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        
        entry = {
            "id": content_hash,
            "content": content,
            "source_type": source_type,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "stored_locally": True
        }
        
        # Check if already exists
        exists = False
        for i, existing_entry in enumerate(data):
            if existing_entry["id"] == content_hash:
                data[i] = entry  # Update existing
                exists = True
                break
        
        if not exists:
            data.append(entry)
        
        try:
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return content_hash
        except Exception as e:
            print(f"Error saving to local storage: {e}")
            return ""
    
    def search_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant context based on the query"""
        try:
            # For now, just fetch recent entries - in a real implementation,
            # you'd use vector search or full-text search
            response = self.supabase.table(self.table_name).select("*").order("created_at", desc=True).limit(top_k).execute()
            return response.data
        except Exception as e:
            print(f"Error searching context in Supabase: {e}")
            # Fallback to local search
            return self._search_local_context(query, top_k)
    
    def _search_local_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """Fallback to local context search if Supabase fails"""
        storage_file = "rag_storage.json"
        if not os.path.exists(storage_file):
            return []
        
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Simple keyword matching
            query_words = query.lower().split()
            scored_entries = []
            
            for entry in data:
                content_lower = entry["content"].lower()
                score = sum(1 for word in query_words if word in content_lower)
                
                if score > 0:
                    scored_entries.append((entry, score))
            
            # Sort by score
            scored_entries.sort(key=lambda x: x[1], desc=True)
            return [entry for entry, score in scored_entries[:top_k]]
        except Exception as e:
            print(f"Error searching local context: {e}")
            return []

# Global instance
try:
    supabase_rag = SupabaseRAGStorage()
except ValueError:
    # If Supabase credentials aren't available, use local storage only
    supabase_rag = None

def get_rag_context(query: str = "") -> str:
    """Get relevant context from RAG storage for a given query"""
    if not supabase_rag:
        # Use local storage if Supabase is not configured
        storage_file = "rag_storage.json"
        if not os.path.exists(storage_file):
            return ""
        
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                return ""
            
            # Return most recent entries
            recent_entries = data[-5:]
            return "\n".join([entry["content"] for entry in recent_entries])
        except:
            return ""
    
    if query:
        relevant_entries = supabase_rag.search_context(query)
    else:
        relevant_entries = supabase_rag.search_context("", top_k=5)
    
    if not relevant_entries:
        return ""
    
    combined_context = ""
    for entry in relevant_entries:
        content = entry.get("content", "")
        combined_context += f"\n--- Context Source ---\n{content}\n----------------------\n"
    
    return combined_context.strip()

def add_conversation_to_rag(user_message: str, ai_response: str, session_id: str = None) -> str:
    """Add a conversation turn to RAG storage"""
    content = f"User: {user_message}\nAI: {ai_response}"
    metadata = {
        "session_id": session_id,
        "type": "conversation_turn",
        "user_message": user_message,
        "ai_response": ai_response
    }
    
    if supabase_rag:
        return supabase_rag.add_context(content, "conversation", metadata)
    else:
        # Use local storage
        import hashlib
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        
        storage_file = "rag_storage.json"
        data = []
        
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []
        
        # Check if already exists
        exists = False
        for i, existing_entry in enumerate(data):
            if existing_entry["id"] == content_hash:
                data[i] = {
                    "id": content_hash,
                    "content": content,
                    "source_type": "conversation",
                    "metadata": metadata,
                    "created_at": datetime.now().isoformat(),
                    "stored_locally": True
                }
                exists = True
                break
        
        if not exists:
            data.append({
                "id": content_hash,
                "content": content,
                "source_type": "conversation",
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "stored_locally": True
            })
        
        try:
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to local storage: {e}")
        
        return content_hash
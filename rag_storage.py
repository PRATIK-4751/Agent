"""
Simple RAG Storage System using local JSON file to mimic Supabase functionality
"""
import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional


class SimpleRAGStorage:
    """
    A simple RAG (Retrieval Augmented Generation) storage system that uses local JSON files
    to store and retrieve contextual information for AI conversations.
    This serves as a local alternative to Supabase RAG functionality.
    """
    
    def __init__(self, storage_file: str = "rag_storage.json"):
        self.storage_file = storage_file
        self.data = self.load_data()
    
    def load_data(self) -> List[Dict]:
        """Load data from the storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_data(self):
        """Save data to the storage file"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_context(self, content: str, source_type: str = "general", metadata: Dict = None) -> str:
        """Add content as context to the RAG storage"""
        if not metadata:
            metadata = {}
        
        # Create a hash-based ID for the content
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        
        entry = {
            "id": content_hash,
            "content": content,
            "source_type": source_type,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        # Check if this content already exists (avoid duplicates)
        for existing_entry in self.data:
            if existing_entry["id"] == content_hash:
                return content_hash
        
        self.data.append(entry)
        self.save_data()
        return content_hash
    
    def search_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant context based on the query"""
        if not query:
            return []
        
        # Simple keyword matching - rank entries by how many query words appear in the content
        query_words = query.lower().split()
        scored_entries = []
        
        for entry in self.data:
            content_lower = entry["content"].lower()
            score = sum(1 for word in query_words if word in content_lower)
            
            if score > 0:
                scored_entries.append((entry, score))
        
        # Sort by score (descending)
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k entries
        return [entry for entry, score in scored_entries[:top_k]]
    
    def get_all_context(self) -> List[Dict]:
        """Get all stored context"""
        return self.data[:]
    
    def clear_context(self):
        """Clear all stored context"""
        self.data = []
        self.save_data()
    
    def add_conversation_context(self, user_message: str, ai_response: str, session_id: str = None):
        """Add a conversation turn as context"""
        content = f"User: {user_message}\nAI: {ai_response}"
        metadata = {
            "session_id": session_id,
            "type": "conversation_turn",
            "user_message": user_message,
            "ai_response": ai_response
        }
        
        return self.add_context(content, "conversation", metadata)
    
    def add_document_context(self, document_content: str, doc_name: str = None):
        """Add document content as context"""
        metadata = {
            "doc_name": doc_name,
            "type": "document"
        }
        
        return self.add_context(document_content, "document", metadata)
    
    def get_relevant_context_for_query(self, query: str, max_length: int = 2000) -> str:
        """Get relevant context for a query, with length limiting"""
        relevant_entries = self.search_context(query, top_k=10)
        
        if not relevant_entries:
            return ""
        
        combined_context = ""
        for entry in relevant_entries:
            entry_text = f"\n--- Context Source ---\n{entry['content']}\n----------------------\n"
            
            # Check if adding this entry would exceed the max length
            if len(combined_context) + len(entry_text) > max_length:
                break
            
            combined_context += entry_text
        
        return combined_context.strip()


# Global instance for easy access
rag_storage = SimpleRAGStorage()


def get_rag_context(query: str = "") -> str:
    """Get relevant context from RAG storage for a given query"""
    if query:
        return rag_storage.get_relevant_context_for_query(query)
    else:
        # Return recent context if no specific query
        all_context = rag_storage.get_all_context()
        if all_context:
            # Return the most recent entries
            recent_entries = all_context[-5:]  # Last 5 entries
            return "\n".join([entry["content"] for entry in recent_entries])
        return ""


def add_to_rag(content: str, source_type: str = "general", metadata: Dict = None) -> str:
    """Add content to RAG storage"""
    return rag_storage.add_context(content, source_type, metadata)


def add_conversation_to_rag(user_message: str, ai_response: str, session_id: str = None) -> str:
    """Add a conversation turn to RAG storage"""
    return rag_storage.add_conversation_context(user_message, ai_response, session_id)


def add_document_to_rag(document_content: str, doc_name: str = None) -> str:
    """Add document content to RAG storage"""
    return rag_storage.add_document_context(document_content, doc_name)


if __name__ == "__main__":
    # Example usage
    print("Testing RAG storage...")
    
    # Add some sample content
    sample_content = "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
    add_to_rag(sample_content, "knowledge_base", {"topic": "ML"})
    
    # Search for relevant context
    query = "artificial intelligence"
    context = get_rag_context(query)
    print(f"Query: {query}")
    print(f"Relevant context: {context}")
    
    print("\nRAG storage initialized successfully!")
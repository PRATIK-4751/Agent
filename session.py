import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def save_message(session_id: str, role: str, content: str, image_url: str = None):
    
    session_payload = {"session_id": session_id}
    requests.post(
        f"{SUPABASE_URL}/rest/v1/chat_sessions",
        headers=HEADERS,
        json=session_payload
    )
    
    # Save message
    message_payload = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "image_url": image_url
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/chat_messages",
        headers=HEADERS,
        json=message_payload
    )
    
    return r.status_code in [200, 201]

def get_session_history(session_id: str, limit: int = 20) -> List[Dict]:
    
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/chat_messages",
        headers=HEADERS,
        params={
            "session_id": f"eq.{session_id}",
            "order": "created_at.asc",
            "limit": limit
        }
    )
    
    if r.status_code == 200:
        return r.json()
    
    return []
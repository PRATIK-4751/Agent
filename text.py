import os
from typing import List, Dict
from dotenv import load_dotenv
import requests
from pratik_prompt import get_pratik_context

load_dotenv()

SYSTEM_PROMPT = f"""You are an AI assistant named "Pratik AI Agent" created by Pratik Raj. 
IMPORTANT: You are NOT ChatGPT, NOT OpenAI, NOT Claude, NOT any other AI. You are Pratik's personal AI Agent.

About your creator Pratik Raj:
{get_pratik_context()}

Instructions:
- Always introduce yourself as "Pratik AI Agent" or "Pratik's AI Assistant"
- When asked who made you or who you are, say you were created by Pratik Raj
- Be helpful, concise, and friendly
- Never claim to be ChatGPT, OpenAI, Anthropic, or any other AI company's product"""

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

OPENROUTER_TEXT_MODELS = [
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "qwen/qwen-2.5-vl-7b-instruct:free",
    "allenai/molmo-2-8b:free"
]

OLLAMA_CLOUD_MODELS = [
    "gpt-oss:120b-cloud",
    "gpt-oss:20b-cloud",
    "deepseek-v3.1:671b-cloud",
    "qwen3-coder:480b-cloud"
]

class TextResponseHandler:
    def __init__(self):
        self.context_window: List[Dict[str, str]] = []
        self.max_context_length = 20
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.ollama_cloud_url = os.getenv("OLLAMA_CLOUD_URL", "https://ollama.com")
        self.ollama_cloud_api_key = os.getenv("OLLAMA_CLOUD_API_KEY")
        
    def add_message_to_context(self, role: str, content: str):
        self.context_window.append({"role": role, "content": content})
        if len(self.context_window) > self.max_context_length:
            self.context_window.pop(0)
    
    def clear_context(self):
        self.context_window.clear()
    
    def get_context_messages(self) -> List[Dict[str, str]]:
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
        msgs.extend(self.context_window.copy())
        return msgs
    
    def get_response_ollama_cloud(self, prompt: str) -> str:
        if not self.ollama_cloud_api_key:
            return None
        
        self.add_message_to_context("user", prompt)
        messages = self.get_context_messages()
        
        for model in OLLAMA_CLOUD_MODELS:
            try:
                response = requests.post(
                    f"{self.ollama_cloud_url}/api/chat",
                    headers={
                        "Authorization": f"Bearer {self.ollama_cloud_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"model": model, "messages": messages, "stream": False},
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('message', {}).get('content', '')
                    if response_text:
                        self.add_message_to_context("assistant", response_text)
                        return response_text
            except:
                continue
        return None
    
    def get_response_local(self, prompt: str) -> str:
        if not OLLAMA_AVAILABLE:
            result = self.get_response_ollama_cloud(prompt)
            if result:
                return result
            return self.get_response_online(prompt)
        
        self.add_message_to_context("user", prompt)
        messages = self.get_context_messages()
        
        local_models = ["llava:7b", "tinyllama:latest"]
        for model in local_models:
            try:
                response = ollama.chat(model=model, messages=messages)
                response_text = response['message']['content']
                self.add_message_to_context("assistant", response_text)
                return response_text
            except:
                continue
        
        result = self.get_response_ollama_cloud(prompt)
        if result:
            return result
        return self.get_response_online(prompt)
    
    def get_response_online(self, prompt: str) -> str:
        result = self.get_response_ollama_cloud(prompt)
        if result:
            return result
        
        if not self.openrouter_api_key:
            if OLLAMA_AVAILABLE:
                return self.get_response_local(prompt)
            return "API key not configured. Please set OPENROUTER_API_KEY."
        
        self.add_message_to_context("user", prompt)
        messages = self.get_context_messages()
        
        for model in OPENROUTER_TEXT_MODELS:
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": 1024}
                )
                
                if response.status_code != 200:
                    continue
                
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    response_text = result['choices'][0].get('message', {}).get('content', '')
                    if response_text:
                        self.add_message_to_context("assistant", response_text)
                        return response_text
            except:
                continue
        
        return "Error: All models failed"
    
    def get_response(self, prompt: str, use_local: bool = False, model: str = None) -> str:
        if use_local:
            return self.get_response_local(prompt)
        else:
            return self.get_response_online(prompt)

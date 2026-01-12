import os
from typing import List, Dict
from dotenv import load_dotenv
import requests
import json

load_dotenv()

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Install ollama for local model support: pip install ollama")

class TextResponseHandler:
    def __init__(self):
        self.context_window: List[Dict[str, str]] = []
        self.max_context_length = 20
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
    def add_message_to_context(self, role: str, content: str):
        self.context_window.append({"role": role, "content": content})
        if len(self.context_window) > self.max_context_length:
            self.context_window.pop(0)
    
    def clear_context(self):
        self.context_window.clear()
    
    def get_context_messages(self) -> List[Dict[str, str]]:
        return self.context_window.copy()
    
    def get_response_local(self, prompt: str, model: str = "llava:7b") -> str:
        if not OLLAMA_AVAILABLE:
            return "Ollama not available. Install with: pip install ollama"
        
        try:
            self.add_message_to_context("user", prompt)
            messages = self.get_context_messages()
            response = ollama.chat(model=model, messages=messages)
            response_text = response['message']['content']
            self.add_message_to_context("assistant", response_text)
            return response_text
        except Exception as e:
            fallback_models = ["gpt-oss:20b-cloud", "gpt-oss:120b-cloud"]
            messages = self.get_context_messages()
            for fallback_model in fallback_models:
                try:
                    response = ollama.chat(model=fallback_model, messages=messages)
                    response_text = response['message']['content']
                    self.add_message_to_context("assistant", response_text)
                    return response_text
                except:
                    continue
            
            error_msg = f"Error with local model {model}: {str(e)}"
            self.add_message_to_context("assistant", error_msg)
            return error_msg
    
    def get_response_online(self, prompt: str, model: str = "google/gemma-3-27b-it:free") -> str:
        if not self.openrouter_api_key:
            # Fallback to a local model if online API key is not available
            try:
                if OLLAMA_AVAILABLE:
                    response = ollama.chat(model="llava:7b", messages=[{"role": "user", "content": prompt}])
                    response_text = response['message']['content']
                    self.add_message_to_context("assistant", response_text)
                    return response_text
                else:
                    return "API key not configured and Ollama not available. Please configure environment variables."
            except Exception as e:
                return f"API key not configured and fallback failed: {str(e)}"
        
        try:
            self.add_message_to_context("user", prompt)
            messages = self.get_context_messages()
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.text}")
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                if 'message' in result['choices'][0] and 'content' in result['choices'][0]['message']:
                    response_text = result['choices'][0]['message']['content']
                elif 'text' in result['choices'][0]:
                    response_text = result['choices'][0]['text']
                else:
                    response_text = str(result['choices'][0])
            else:
                response_text = str(result)
            
            self.add_message_to_context("assistant", response_text)
            return response_text
        except Exception as e:
            fallback_models = ["gpt-oss:20b-cloud", "gpt-oss:120b-cloud"]
            for fallback_model in fallback_models:
                try:
                    payload["model"] = fallback_model
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code != 200:
                        continue
                    
                    result = response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        if 'message' in result['choices'][0] and 'content' in result['choices'][0]['message']:
                            response_text = result['choices'][0]['message']['content']
                        elif 'text' in result['choices'][0]:
                            response_text = result['choices'][0]['text']
                        else:
                            response_text = str(result['choices'][0])
                    else:
                        response_text = str(result)
                    
                    self.add_message_to_context("assistant", response_text)
                    return response_text
                except:
                    continue
            
            error_msg = f"Error with online model {model}: {str(e)}"
            self.add_message_to_context("assistant", error_msg)
            return error_msg
    
    def get_response(self, prompt: str, use_local: bool = True, model: str = None) -> str:
        if use_local:
            local_model = model or "llava:7b"
            return self.get_response_local(prompt, local_model)
        else:
            online_model = model or "google/gemma-3-27b-it:free"
            return self.get_response_online(prompt, online_model)
    
    def get_context_summary(self) -> str:
        if not self.context_window:
            return "Context window is empty."
        
        summary = f"Context Window ({len(self.context_window)} messages):\n"
        for i, msg in enumerate(self.context_window):
            role = msg['role'].upper()
            content_preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            summary += f"{i+1}. [{role}] {content_preview}\n"
        
        return summary


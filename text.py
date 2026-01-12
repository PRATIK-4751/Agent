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
            return "OpenRouter API key not configured in environment."
        
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

if __name__ == "__main__":
    handler = TextResponseHandler()
    print("Text Response Handler - Interactive Mode")
    print("=========================================")
    print(f"Local Ollama available: {OLLAMA_AVAILABLE}")
    print(f"OpenRouter API configured: {bool(handler.openrouter_api_key)}")
    
    current_mode = None
    
    while True:
        # If not in a chat mode, show mode selection
        if current_mode is None:
            print("\nChoose mode:")
            print("1. Local model (llava:7b)")
            print("2. Online model (google/gemma-3-27b-it:free)")
            print("3. View context")
            print("4. Clear context")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "5":
                print("Exiting...")
                break
            elif choice == "3":
                print(f"\n{handler.get_context_summary()}")
            elif choice == "4":
                handler.clear_context()
                print("Context cleared.")
            elif choice in ["1", "2"]:
                current_mode = "local" if choice == "1" else "online"
                print(f"\nEntering {'LOCAL' if current_mode == 'local' else 'ONLINE'} chat mode. Type 'exit' to return to mode selection.")
            else:
                print("Invalid choice. Please enter 1-5.")
        else:
            # In chat mode, continue conversation
            prompt = input("\nYou: ")
            
            # Check for special commands
            if prompt.lower() == "exit":
                current_mode = None
                continue
            elif prompt.lower() == "view context":
                print(f"\n{handler.get_context_summary()}")
                continue
            elif prompt.lower() == "clear context":
                handler.clear_context()
                print("Context cleared.")
                continue
            elif prompt.lower() == "switch mode":
                current_mode = None
                continue
            
            print("Processing...")
            use_local = current_mode == "local"
            response = handler.get_response(prompt, use_local=use_local)
            print(f"AI: {response}")
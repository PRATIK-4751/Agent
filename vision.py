import os
from dotenv import load_dotenv
import requests
import base64

load_dotenv()

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

def analyze_local(image_path, prompt):
    if not OLLAMA_AVAILABLE:
        return "Ollama not available. Install with: pip install ollama"
    
    try:
        with open(image_path, 'rb') as img_file:
            img_bytes = img_file.read()
        
        response = ollama.generate(
            model="moondream:1.8b",
            prompt=prompt,
            images=[img_bytes]
        )
        return response['response']
    except Exception as e:
        fallback_models = ["gpt-oss:20b-cloud", "gpt-oss:120b-cloud"]
        for fallback_model in fallback_models:
            try:
                response = ollama.chat(
                    model=fallback_model,
                    messages=[{"role": "user", "content": f"Image description task: {prompt}"}]
                )
                return response['message']['content']
            except:
                continue
        
        return f"Error: {str(e)}"

def analyze_online(image_path, prompt):
    if not openrouter_api_key:
        return "OpenRouter API key not configured."
    
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }]
        
        payload = {
            "model": "google/gemma-3-27b-it:free",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            return f"API Error: {response.text}"
        
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        fallback_models = ["gpt-oss:20b-cloud", "gpt-oss:120b-cloud"]
        
        for fallback_model in fallback_models:
            try:
                payload = {
                    "model": fallback_model,
                    "messages": [{"role": "user", "content": f"Image description task: {prompt}"}],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    continue
                
                result = response.json()
                return result['choices'][0]['message']['content']
            except:
                continue
        
        return f"Error: {str(e)}"

def vision_to_text(image_path, prompt, vision_local=True, text_local=True):
    if vision_local:
        vision_result = analyze_local(image_path, f"Describe this image in detail: {prompt}")
    else:
        vision_result = analyze_online(image_path, f"Describe this image in detail: {prompt}")
    
    text_prompt = f"Based on this image description: '{vision_result}', {prompt}"
    
    try:
        if text_local and OLLAMA_AVAILABLE:
            text_response = ollama.chat(
                model="llava:7b",
                messages=[{"role": "user", "content": text_prompt}]
            )
            return text_response['message']['content']
        else:
            if openrouter_api_key:
                payload = {
                    "model": "google/gemma-3-27b-it:free",
                    "messages": [{"role": "user", "content": text_prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
                
                headers = {
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    return f"API Error: {response.text}"
            else:
                return vision_result
    except Exception as e:
        return f"Text processing error: {str(e)}, Vision result: {vision_result}"


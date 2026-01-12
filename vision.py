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
ollama_cloud_url = os.getenv("OLLAMA_CLOUD_URL", "https://ollama.com")
ollama_cloud_api_key = os.getenv("OLLAMA_CLOUD_API_KEY")

OPENROUTER_VISION_MODEL = "allenai/molmo-2-8b:free"
OLLAMA_CLOUD_MODELS = [
    "gpt-oss:120b-cloud",
    "gpt-oss:20b-cloud",
    "deepseek-v3.1:671b-cloud",
    "qwen3-coder:480b-cloud"
]

def get_ollama_cloud_response(prompt):
    if not ollama_cloud_api_key:
        return None
    
    for model in OLLAMA_CLOUD_MODELS:
        try:
            response = requests.post(
                f"{ollama_cloud_url}/api/chat",
                headers={
                    "Authorization": f"Bearer {ollama_cloud_api_key}",
                    "Content-Type": "application/json"
                },
                json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('message', {}).get('content', '')
                if content:
                    return content
        except:
            continue
    return None

def analyze_local(image_path, prompt):
    if not OLLAMA_AVAILABLE:
        return analyze_online(image_path, prompt)
    
    try:
        with open(image_path, 'rb') as img_file:
            img_bytes = img_file.read()
        
        response = ollama.generate(model="moondream:1.8b", prompt=prompt, images=[img_bytes])
        return response['response']
    except Exception as e:
        cloud_result = get_ollama_cloud_response(f"Image description task: {prompt}")
        if cloud_result:
            return cloud_result
        return analyze_online(image_path, prompt)

def analyze_online(image_path, prompt):
    cloud_result = get_ollama_cloud_response(f"Image description task: {prompt}")
    if cloud_result:
        return cloud_result
    
    if not openrouter_api_key:
        return "OpenRouter API key not configured. Please set OPENROUTER_API_KEY."
    
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": OPENROUTER_VISION_MODEL,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                "temperature": 0.7,
                "max_tokens": 1024
            }
        )
        
        if response.status_code != 200:
            return f"API Error: {response.text}"
        
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def vision_to_text(image_path, prompt, vision_local=False, text_local=False):
    if vision_local and OLLAMA_AVAILABLE:
        vision_result = analyze_local(image_path, f"Describe this image in detail: {prompt}")
    else:
        vision_result = analyze_online(image_path, f"Describe this image in detail: {prompt}")
    
    text_prompt = f"Based on this image description: '{vision_result}', {prompt}"
    
    try:
        cloud_result = get_ollama_cloud_response(text_prompt)
        if cloud_result:
            return cloud_result
        
        if text_local and OLLAMA_AVAILABLE:
            try:
                text_response = ollama.chat(model="llava:7b", messages=[{"role": "user", "content": text_prompt}])
                return text_response['message']['content']
            except:
                pass
        
        if openrouter_api_key:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENROUTER_VISION_MODEL,
                    "messages": [{"role": "user", "content": text_prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
        
        return vision_result
    except Exception as e:
        return f"Error: {str(e)}, Vision result: {vision_result}"

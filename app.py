import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava:7b"

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def ask_ollama(system_prompt, user_prompt, image_path=None):
    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False
    }
    if image_path:
        payload["images"] = [encode_image(image_path)]
    res = requests.post(OLLAMA_URL, json=payload)
    if res.status_code != 200:
        raise Exception(res.text)
    return res.json()["response"]

def ask_openrouter(system_prompt, user_prompt, image_path=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Vision-Agent"
    }

    content = [{"type": "text", "text": user_prompt}]

    if image_path:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
            }
        })

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]
    }

    res = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    if res.status_code != 200:
        raise Exception(res.text)
    return res.json()["choices"][0]["message"]["content"]

def ask(provider, system_prompt, user_prompt, image_path=None):
    if provider == "local":
        return ask_ollama(system_prompt, user_prompt, image_path)
    if provider == "online":
        return ask_openrouter(system_prompt, user_prompt, image_path)
    raise Exception("Invalid provider")

if __name__ == "__main__":
    print("Vision LLM Pipeline !\n")

    provider = input("Choose LLM [local / online] =>> ").strip().lower()
    system_prompt = input("System Prompt =>> ").strip()
    user_prompt = input("User Prompt =>> ").strip()
    image_path = input("Image path (enter to skip) =>> ").strip()

    if not system_prompt:
        system_prompt = "You are a helpful AI assistant."

    if not image_path:
        image_path = None

    response = ask(provider, system_prompt, user_prompt, image_path)

    print("\nAI =>>\n")
    print(response)

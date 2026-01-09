import requests
import base64
import os
from dotenv import load_dotenv
load_dotenv()
PROVIDER = "openrouter"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava:7b"

SYSTEM_PROMPT = """
You are a vision-language assistant.

You MUST base your answers strictly on the provided image.
Do NOT assume the image is a photograph.
The image may be an illustration, painting, anime-style art, or stylized scene.

Rules:
- First determine whether the image is a photo, artwork, illustration, or digital art.
- Describe only what is visually present.
- Mention colors, shapes, environment, and style.
- If something is unclear, say it is unclear instead of guessing.
- Do NOT hallucinate objects, buildings, or people.
- If the image appears artistic, describe the art style and mood.
- Be precise, calm, and factual.
"""

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def ask_ollama(prompt, image_path=None):
    payload = {
        "model": OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False
    }
    if image_path:
        payload["images"] = [encode_image(image_path)]
    res = requests.post(OLLAMA_URL, json=payload)
    if res.status_code != 200:
        raise Exception(res.text)
    return res.json()["response"]

def ask_openrouter(prompt, image_path=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Local Vision Agent"
    }

    content = [{"type": "text", "text": prompt}]

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
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content}
        ]
    }

    res = requests.post(OPENROUTER_URL, headers=headers, json=payload)

    if res.status_code != 200:
        raise Exception(res.text)

    return res.json()["choices"][0]["message"]["content"]


def ask(prompt, image_path=None):
    if PROVIDER == "ollama":
        return ask_ollama(prompt, image_path)
    if PROVIDER == "openrouter":
        return ask_openrouter(prompt, image_path)
    raise Exception("Invalid provider")

if __name__ == "__main__":
    print("Talking to Vision LLM")
    user_input = input("Ask Anything =>> ")
    reply = ask(user_input)
    question = "describe the picture in detail"
    answer = ask(question, image_path="picture.jpg")
    print("Pratik:->>", user_input)
    print("OLLAMA/GEMMA:->>", reply)
    print("question:->>", question)
    print("OLLAMA/GEMMA:->>", answer)

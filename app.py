import requests
import json 

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llava:7b"

def ask(prompt):
    payload = {
        "model"  : MODEL_NAME,
        "prompt" : prompt,
        "stream" : False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code !=200:
        raise Exception(" there is an error in the ollama ! ")
    
    data = response.json()
    return data["response"]

if __name__ == "__main__":
    print("Talking to Local LLM via OLLAMA !~")
    user_input = input("Ask Anything =>> ")
    reply = ask(user_input)
    print("Pratik:->>",user_input)
    print("OLLAMA:->>",reply)

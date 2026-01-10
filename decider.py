import json
from typing import Dict, List, Tuple, Any, Optional

def memory_decider(
    ask_fn,
    provider: str,
    system_prompt: str,
    user_message: str,
    ai_response: str,
    image_included: bool = False,
    conversation_history: List[Tuple[str, str]] = None
) -> Optional[Dict[str, Any]]:
    
    
    context = ""
    if conversation_history:
        context = "\n".join([f"{r.upper()}: {t}" for r, t in conversation_history[-4:]])
    
    image_note = "An image was included in this exchange." if image_included else ""
    
    decider_prompt = f"""
You are a memory evaluation system for an AI assistant. Analyze this conversation and decide what to remember.

CONVERSATION CONTEXT:
{context}

CURRENT EXCHANGE:
User: {user_message}
{image_note}
AI: {ai_response}

RULES:
1. DON'T store: greetings, thanks, "ok", "got it", small talk, generic responses
2. DO store: 
   - Facts about the user (preferences, background, goals)
   - Important decisions or plans
   - Image descriptions and their context
   - Key information from documents/images
   - Specific requests or requirements
   - Meaningful conversation summaries

3. If the exchange adds nothing memorable, return: {{"store": false}}

4. Memory types:
   - user_pref: User preferences, likes/dislikes
   - fact: Factual information about user, world, or topic
   - goal: User's goals, objectives, or intentions
   - decision: Decisions made or plans created
   - image_desc: Description of analyzed image with context
   - insight: Important insight or realization

5. Importance (1-5):
   - 1: Minor detail
   - 3: Useful information
   - 5: Critical information

OUTPUT ONLY THIS JSON FORMAT (no markdown, no explanations):
{{
  "store": true,
  "type": "memory_type",
  "importance": 3,
  "summary": "concise memory"
}}

OR if nothing to store:
{{"store": false}}
""".strip()

    try:
        result = ask_fn(
            provider,
            system_prompt="You are a JSON-only response system. Output valid JSON with no markdown or explanations.",
            user_prompt=decider_prompt
        )
        
        result = str(result).strip()
        
        if result.startswith("```json"):
            result = result[7:]
        elif result.startswith("```"):
            result = result[3:]
        
        if result.endswith("```"):
            result = result[:-3]
        
        result = result.strip()
        
        start_idx = result.find('{')
        end_idx = result.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            print(f"No JSON found in response: {result[:100]}")
            return None
        
        json_str = result[start_idx:end_idx+1]
        decision = json.loads(json_str)
        
        if not isinstance(decision, dict):
            print(f"Decision is not a dict: {type(decision)}")
            return None
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response was: {result[:200]}")
        return None
    except Exception as e:
        print(f"Decider error: {e}")
        return None

    if not isinstance(decision, dict):
        return None
        
    if not decision.get("store"):
        return None

    if not decision.get("summary") or not decision.get("type"):
        return None

    importance = decision.get("importance", 1)
    if not isinstance(importance, int) or importance < 1 or importance > 5:
        importance = 3

    return {
        "content": decision["summary"],
        "mem_type": decision["type"],
        "importance": importance
    }
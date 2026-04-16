import requests
import time
import dotenv
import os
dotenv.load_dotenv()

# Your Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print(OPENROUTER_API_KEY)
def call_llm(prompt, mode="short", max_tokens=None):
    """
    mode: "short" or "long" (Models like Llama 3.1 8B Free support up to 128k context)
    max_tokens: limits the output length
    """
    # Using the :free suffix ensures you aren't charged
    # Llama 3.1 8B Free supports 128k context
    model_id = "nvidia/nemotron-3-super-120b-a12b:free"
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000", # Optional but recommended
    }

    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }

    # OpenRouter uses 'max_tokens' instead of Ollama's 'num_predict'
    if max_tokens:
        payload["max_tokens"] = max_tokens

    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_json = response.json()
        end_time = time.time()

        content = res_json['choices'][0]['message']['content']
        
        # OpenRouter provides usage stats in the 'usage' field
        usage = res_json.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        response_tokens = usage.get('completion_tokens', 0)
        
        # Calculate tokens per second (t/s) manually
        total_duration = end_time - start_time
        tps = response_tokens / total_duration if total_duration > 0 else 0

        print(f"--- [Stats] {tps:.2f} t/s | In: {prompt_tokens} | Out: {response_tokens} ---")

        return content

    except Exception as e:
        print(f"Error calling OpenRouter: {e}")
        return None

# Usage example:
# result = call_openrouter_llm("Explain quantum physics simply", mode="long", max_tokens=500)
# print(result)
    

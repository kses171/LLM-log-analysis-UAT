import requests
import json
import logging

logger = logging.getLogger(__name__)

def call_local_llm(model_name, conversation_text, temperature=0.7, max_tokens=512):
    payload = {
        "model": model_name,
        "prompt": conversation_text,
        "stream": True,  # enable streaming
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    reply = ""
    try:
        with requests.post("http://localhost:11434/api/generate", json=payload, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        if "response" in data:
                            reply += data["response"]
                            yield reply  # stream partial responses
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.exception(f"Error calling local Ollama API: {e}")
        yield f"Error: {e}"

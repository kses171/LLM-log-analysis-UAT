import json
import logging
import boto3
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache clients by region to avoid re-creating them repeatedly
_clients = {}

def get_bedrock_client(region_name: str = "us-east-1"):
    if region_name not in _clients:
        _clients[region_name] = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
    return _clients[region_name]    


def call_bedrock(
    model_id: str,
    conversation_text: str,
    temperature: float = 0.6,
    max_tokens: int = 512,
    region_name: str = "us-east-1"
):  
    # Split conversation_text by lines and map "User:" / "Bot:" prefixes
    formatted = "<|begin_of_sentence|>"
    for line in conversation_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("User:"):
            formatted += f"<|User|>{line[len('User:'):].strip()}"
        elif line.startswith("Bot:"):
            formatted += f"<|Assistant|>{line[len('Bot:'):].strip()}"
        else:
            # For system prompt or other context
            formatted += f"{line}"

    # Always end with assistant ready to reply
    formatted += "<|Assistant|><think>\n"

    # Prepare DeepSeek request
    native_request = {
        "prompt": formatted,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    # logger.info("Formatted prompt:\n%s", formatted)
    # logger.info("JSON request:\n%s", json.dumps(native_request, indent=2))

    try:
        bedrock_runtime = get_bedrock_client(region_name)
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(native_request)
        )

        model_response = json.loads(response['body'].read())
        choices = model_response.get("choices", [])

        if not choices:
            yield "Error: No response choices returned from model"
            return

        generation = choices[0].get("text", "").strip()
        yield generation

    except Exception as e:
        logger.exception(f"Error calling Bedrock API: {e}")
        yield f"Error: {e}"


## for debugging & sanity check
if __name__ == "__main__":
    for reply in call_bedrock(
        model_id="us.deepseek.r1-v1:0",  # example DeepSeek Bedrock model ID
        conversation_text="Hello from DeepSeek on Bedrock!"
    ):
        print("Reply:", reply)

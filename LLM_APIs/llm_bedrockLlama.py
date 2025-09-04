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
    max_gen_len: int = 512,
    region_name: str = "us-east-1"
):  
    # Build conversation in Llama format
    formatted = "<|begin_of_text|>"
    
    # Parse conversation text and format for Llama
    lines = conversation_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("User:"):
            user_content = line[len('User:'):].strip()
            formatted += f"<|start_header_id|>user<|end_header_id|>\n\n{user_content}\n\n<|eot_id|>"
        elif line.startswith("Bot:"):
            bot_content = line[len('Bot:'):].strip()
            formatted += f"<|start_header_id|>assistant<|end_header_id|>\n\n{bot_content}\n\n<|eot_id|>"
        else:
            # For system prompt or other context - treat as user message
            formatted += f"<|start_header_id|>user<|end_header_id|>\n\n{line}\n\n<|eot_id|>"

    # End with assistant ready to reply
    formatted += "<|start_header_id|>assistant<|end_header_id|>\n\n"

    # Prepare Llama request
    native_request = {
        "prompt": formatted,
        "max_gen_len": max_gen_len,
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
        generation = model_response.get("generation", "").strip()
        
        if not generation:
            yield "Error: No generation returned from model"
            return

        yield generation

    except Exception as e:
        logger.exception(f"Error calling Bedrock API: {e}")
        yield f"Error: {e}"


## for debugging & sanity check
if __name__ == "__main__":
    for reply in call_bedrock(
        model_id="us.meta.llama4-maverick-17b-instruct-v1:0",  # example Llama Bedrock model ID
        conversation_text="User: Hello from Llama on Bedrock!"
    ):
        print("Reply:", reply)
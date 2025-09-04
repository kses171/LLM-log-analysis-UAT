import json
import logging
import boto3

logger = logging.getLogger(__name__)

# Cache clients by region to avoid re-creating them repeatedly
_clients = {}

def get_bedrock_client(region_name: str = "ap-southeast-1"):
    if region_name not in _clients:
        _clients[region_name] = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
    return _clients[region_name]    

def call_bedrock(
    model_id: str,
    conversation_text: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
    region_name: str = "ap-southeast-1"
):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": conversation_text}],
            }
        ]   
    }

    try:
        bedrock_runtime = get_bedrock_client(region_name)
        ### non-streaming, change to invoke_model_with_response_stream if streaming desired
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        response_body = json.loads(response['body'].read())
        reply = response_body['content'][0]['text'].strip()
        yield reply
    except Exception as e:
        logger.exception(f"Error calling Bedrock API: {e}")
        yield f"Error: {e}"


## for debugging & sanity check
if __name__ == "__main__":
    for reply in call_bedrock(
        model_id="apac.anthropic.claude-sonnet-4-20250514-v1:0",  # example Bedrock model
        conversation_text="Hello from Bedrock!"
    ):
        print("Reply:", reply)
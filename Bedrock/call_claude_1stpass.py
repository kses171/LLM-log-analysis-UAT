# timeline_generator.py

import boto3
import json
import time
from typing import Optional

def generate_timeline(
    md_filepath: str,
    prompt_filepath: str,
    start_range: int,
    end_range: int,
    log_name: str,
    region: str = 'us-east-1',
    model_id: str = 'us.anthropic.claude-sonnet-4-20250514-v1:0',
    delay_between_calls: float = 8.0,
    long_delay_every: Optional[int] = 7,
    long_delay_duration: float = 100.0,
    max_tokens: int = 9999,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> None:
    """
    Iterate over JSON log parts, call Amazon Bedrock to generate timeline entries,
    and append each part's output to a Markdown file.

    Args:
        md_filepath: Path to the Markdown output file.
        prompt_filepath: Path to the prompt template file (with `{log_json}` placeholder).
        start_range: First part number (inclusive).
        end_range: One past the last part number (exclusive).
        log_name: Subdirectory under "./requestsToLLM2/" where JSON parts live.
        region: AWS region for the Bedrock client.
        model_id: The Bedrock model identifier.
        delay_between_calls: Seconds to sleep between each API call.
        long_delay_every: If provided, after this many parts, sleep an extra long delay.
        long_delay_duration: Duration of the extra long sleep.
        max_tokens: `max_tokens` parameter for the model.
        temperature: Sampling temperature.
        top_p: Nucleus sampling parameter.
    """

    # 1. Write (or overwrite) the file header
    with open(md_filepath, 'w', encoding='utf-8') as md_file:
        md_file.write('# 1st Pass Timeline of Log Activity\n\n')

    # 2. Load prompt template
    with open(prompt_filepath, 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    # 3. Initialize Bedrock client once
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=region  # Change to your preferred region
    )

    for part_number in range(start_range, end_range):
        # Load the JSON log data
        json_path = f'./requestsToLLM/{log_name}/part_{part_number:02d}.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        # Fill in the prompt
        prompt = prompt_template.format(log_json=json.dumps(log_data, indent=2))

        # Prepare native request
        # Prepare the request body
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ]
        }

        # Invoke Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=model_id,  # Change model as needed
            body=json.dumps(body)
        )

        response_body = json.loads(response['body'].read())
        response = response_body['content'][0]['text'].strip()
        print(f"[Part {part_number}] received {len(response)} chars")

        # Append to markdown
        with open(md_filepath, 'a', encoding='utf-8') as md_file:
            md_file.write(f'## Part {part_number}\n\n')
            md_file.write(response + '\n\n')

        # Throttle
        time.sleep(delay_between_calls)
        if long_delay_every and (part_number - start_range + 1) % long_delay_every == 0:
            print(f"Reached {part_number}; pausing {long_delay_duration}s")
            time.sleep(long_delay_duration)

    print(f"All responses written to {md_filepath}")

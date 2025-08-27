# timeline_generator.py
import json
import time
from typing import Optional
import sys
from pathlib import Path

# ──────────────────────────────
# Project imports
# ──────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from LLM_APIs.llm_bedrock import call_bedrock  # <-- use the shared client

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
    """

    # 1. Write (or overwrite) the file header
    with open(md_filepath, 'w', encoding='utf-8') as md_file:
        md_file.write('# 1st Pass Timeline of Log Activity\n\n')

    # 2. Load prompt template
    with open(prompt_filepath, 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    for part_number in range(start_range, end_range):
        # Load the JSON log data
        json_path = f'./requestsToLLM/{log_name}/part_{part_number:02d}.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)

        # Fill in the prompt
        prompt = prompt_template.format(log_json=json.dumps(log_data, indent=2))

        # Use llm_bedrock
        reply = ""
        for chunk in call_bedrock(
            model_id=model_id,
            conversation_text=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            region_name=region
        ):
            reply = chunk  # single final response

        print(f"[Part {part_number}] received {len(reply)} chars")

        # Append to markdown
        with open(md_filepath, 'a', encoding='utf-8') as md_file:
            md_file.write(f'## Part {part_number}\n\n')
            md_file.write(reply + '\n\n')

        # Throttle
        time.sleep(delay_between_calls)
        if long_delay_every and (part_number - start_range + 1) % long_delay_every == 0:
            print(f"Reached {part_number}; pausing {long_delay_duration}s")
            time.sleep(long_delay_duration)

    print(f"All responses written to {md_filepath}")

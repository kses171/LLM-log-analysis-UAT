#!/usr/bin/env python3
import json
import time
from pathlib import Path
from typing import Union
import os
import sys 

# ──────────────────────────────
# Project imports
# ──────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from LLM_APIs.llm_bedrock import call_bedrock  # <-- use the shared client


def generate_flagged_timeline(
    md_filepath: Union[str, Path],
    prompt_filepath: Union[str, Path],
    json_path: Union[str, Path],
    start_range: int = 1,
    end_range: int = 2,
    model_id: str = 'us.anthropic.claude-sonnet-4-20250514-v1:0',
    region: str = 'us-east-1',
    max_tokens: int = 99999,
    temperature: float = 0.7,
    top_p: float = 0.95,
    delay_between_parts: float = 0.0
) -> None:
    """
    Iterate once (or over a small range) to generate a consolidated timeline
    from a flagged-events JSON file, appending each 'part' to an output Markdown.

    Args:
        md_filepath: Path to the output Markdown file.
        prompt_filepath: Path to the prompt template (uses `{log_json}`).
        json_path: Path to the flagged-events JSON file.
        start_range: First part number (inclusive).
        end_range: One past the last part number (exclusive).
        model_id: Bedrock model identifier.
        region: AWS region for Bedrock.
        max_tokens: `max_gen_len` for the model.
        temperature: Sampling temperature.
        top_p: Nucleus sampling parameter.
        delay_between_parts: Seconds to sleep after each part (default 0).
    """
    md_path = Path(md_filepath)
    # 1. Write (or overwrite) header
    md_path.parent.mkdir(parents=True, exist_ok=True)
    with md_path.open('w', encoding='utf-8') as md_file:
        md_file.write('# Timeline of Log Activity\n\n')

    # 2. Load prompt template
    prompt_path = Path(prompt_filepath)
    with prompt_path.open('r', encoding='utf-8') as f:
        prompt_template = f.read()

    for part_number in range(start_range, end_range):
        # Determine the file extension
        _, ext = os.path.splitext(json_path)
        ext = ext.lower()

        # Load and format based on file type
        if ext == ".json":
            # Load JSON data
            with open(json_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            # Fill in the prompt using JSON
            prompt = prompt_template.format(log_json=json.dumps(log_data, indent=2))

        elif ext == ".md":
            # Load Markdown content
            with open(json_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            # Fill in the prompt using Markdown
            # Assuming the template expects a placeholder named 'md_content'
            prompt = prompt_template.format(md_content=md_content)

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
        with md_path.open('a', encoding='utf-8') as md_file:
            md_file.write(f'## Part {part_number}\n\n')
            md_file.write(reply + '\n\n')

        # Optional delay
        if delay_between_parts:
            time.sleep(delay_between_parts)

    print(f"All responses written to {md_filepath}")


if __name__ == "__main__":
    # === CONFIGURE THESE PATHS AND PARAMETERS ===
    MD_FILEPATH      = "./runs/run12/TS-run12.md"
    PROMPT_FILEPATH  = "./prompts2/TS-all-4.txt"
    JSON_PATH        = "./runs/run12/flagged_detailed.json"
    START_RANGE      = 1
    END_RANGE        = 2
    MAX_TOKENS       = 10000
    MODEL_ID         = 'us.anthropic.claude-sonnet-4-20250514-v1:0'
    # ============================================

    generate_flagged_timeline(
        md_filepath=MD_FILEPATH,
        prompt_filepath=PROMPT_FILEPATH,
        json_path=JSON_PATH,
        start_range=START_RANGE,
        end_range=END_RANGE,
        max_tokens=MAX_TOKENS,
        model_id=MODEL_ID
    )

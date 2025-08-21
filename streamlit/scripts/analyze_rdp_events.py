import argparse
import time
import sys
from pathlib import Path
from datetime import datetime

# resolve project root: two levels up from this script file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from Bedrock.call_claude_1stpass import generate_timeline
from Bedrock.call_claude_2ndpass import generate_flagged_timeline
from tools.appendprompts import append_prompts_to_md
from tools.counttokens import count_input_tokens, count_output_tokens


def main(logs_file: Path, prompt1_file: Path, prompt2_file: Path, rdp_param: int):
    # Configuration
    run_id = f"rdp_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    base_runs_dir = Path("./runs")
    run_dir = base_runs_dir / run_id
    LOG_TYPE = 'RDP3'
    MODEL_ID = 'apac.anthropic.claude-sonnet-4-20250514-v1:0'

    # Ensure the run directory exists
    run_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    print("Starting Bedrock queries...")

    ### 1. Generate timeline (first pass)
    first_output_md = run_dir / f"{LOG_TYPE}-{run_id}-1.md"
    generate_timeline(
        md_filepath=first_output_md,
        region="ap-southeast-1",
        prompt_filepath=prompt1_file,
        start_range=1,
        end_range=rdp_param,
        log_name=LOG_TYPE,
        model_id=MODEL_ID,
        max_tokens=10000
    )

    time.sleep(5)

    # 2. Generate flagged timeline (second pass)
    flagged_output_md = run_dir / f"{LOG_TYPE}-{run_id}-3.md"
    generate_flagged_timeline(
        md_filepath=flagged_output_md,
        prompt_filepath=prompt2_file,
        json_path=first_output_md,
        region="ap-southeast-1",
        start_range=1,
        end_range=2,
        max_tokens=10000,
        delay_between_parts=0.0,
        model_id=MODEL_ID
    )

    time.sleep(5)

    end_time = time.time()

    # 3. Token counting
    output_tokens = count_output_tokens(base_runs_dir, run_id, LOG_TYPE)
    input_tokens = count_input_tokens(prompt1_file, prompt2_file, Path(f'./requestsToLLM2/{LOG_TYPE}/'))

    # 4. Append prompts/metadata to final markdown
    append_prompts_to_md(
        md_filepath=flagged_output_md,
        first_prompt_path=prompt1_file,
        second_prompt_path=prompt2_file,
        model_id=MODEL_ID,
        time_taken=end_time - start_time,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )

    print(f"Analysis complete. Outputs saved in: {run_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze RDP event logs and generate timelines.")
    parser.add_argument("logs_path", type=Path, help="Path to the uploaded RDP logs file.")
    parser.add_argument("prompt1_path", type=Path, help="Path to the first prompt file.")
    parser.add_argument("prompt2_path", type=Path, help="Path to the second prompt file.")
    parser.add_argument("rdp_param", type=int, help="Numeric parameter for RDP processing (e.g., number of events).")
    args = parser.parse_args()

    main(
        logs_file=args.logs_path,
        prompt1_file=args.prompt1_path,
        prompt2_file=args.prompt2_path,
        rdp_param=args.rdp_param
    )
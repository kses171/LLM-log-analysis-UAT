import argparse
import time
import sys
import logging
from pathlib import Path
from datetime import datetime

# ──────────────────────────────
# Project imports
# ──────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from Bedrock.call_claude_1stpass import generate_timeline
from Bedrock.call_claude_2ndpass import generate_flagged_timeline
from tools.appendprompts import append_prompts_to_md
from tools.counttokens import count_input_tokens, count_output_tokens
from tools.split_jsonToFit import split_json_by_tokens_and_time
from tools.events_extractor import extract_events
from tools.consolidatorJSON import consolidate

# ──────────────────────────────
# Config & Constants
# ──────────────────────────────
MODEL_ID = "apac.anthropic.claude-sonnet-4-20250514-v1:0"
REGION = "ap-southeast-1"
TOKENS_PER_FILE = 50_000
TIME_GAP_SECONDS = 3600
MAX_TOKENS = 10_000
SLEEP_BETWEEN_STAGES = 5

# ──────────────────────────────
# Helpers
# ──────────────────────────────
def setup_logging(run_dir: Path) -> None:
    """Configure logging to console and file."""
    log_file = run_dir / "pipeline.log"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="w"),
        ],
    )


def split_logs(logs_file: Path) -> tuple[str, Path, int]:
    """Split a large JSON log file into smaller parts."""
    logging.info("Splitting large JSON file...")
    json_name = logs_file.stem
    output_dir = Path("./requestsToLLM") / json_name

    num_parts = split_json_by_tokens_and_time(
        input_file=logs_file,
        output_dir=output_dir,
        tokens_per_file=TOKENS_PER_FILE,
        time_gap_seconds=TIME_GAP_SECONDS,
    )

    logging.info(f"JSON split into {num_parts} parts.")
    return json_name, output_dir, num_parts


def generate_first_pass(run_dir: Path, prompt_file: Path, num_parts: int, json_name: str, temperature: float):
    """Run the first-pass timeline generation."""
    out_path = run_dir / f"{run_dir.name}-1.md"
    generate_timeline(
        md_filepath=out_path,
        region=REGION,
        prompt_filepath=prompt_file,
        start_range=1,
        end_range=num_parts + 1,
        log_name=json_name,
        model_id=MODEL_ID,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
    )
    return out_path


def consolidate_outputs(run_dir: Path) -> Path:
    """Consolidate LLM outputs into a single JSON."""
    out_path = run_dir / "combined.json"
    consolidate(input_dir=run_dir, output_file=out_path)
    return out_path


def extract_flagged_events(run_dir: Path, combined_json: Path, logs_file: Path) -> Path:
    """Extract flagged events into a detailed JSON."""
    out_path = run_dir / "flagged_detailed.json"
    extract_events(flagged_file=combined_json, og_json_path=logs_file, output_file=out_path)
    return out_path


def generate_second_pass(run_dir: Path, prompt_file: Path, flagged_json: Path, temperature: float):
    """Run the second-pass flagged timeline generation."""
    out_path = run_dir / f"{run_dir.name}-2.md"
    generate_flagged_timeline(
        md_filepath=out_path,
        prompt_filepath=prompt_file,
        json_path=flagged_json,
        region=REGION,
        start_range=1,
        end_range=2,
        max_tokens=MAX_TOKENS,
        delay_between_parts=0.0,
        model_id=MODEL_ID,
        temperature=temperature
    )
    return out_path


def finalize_results(
    flagged_output_md: Path,
    first_output_md: Path,
    prompt1_file: Path,
    prompt2_file: Path,
    json_name: str,
    run_dir: Path,
    start_time: float,
) -> None:
    """Perform token counting and append metadata to final output."""
    output_tokens = count_output_tokens(run_dir.parent, run_dir.name)
    input_tokens = count_input_tokens(
        prompt1_file, prompt2_file, Path(f"./requestsToLLM/{json_name}/")
    )
    end_time = time.time()

    append_prompts_to_md(
        md_filepath=flagged_output_md,
        first_prompt_path=prompt1_file,
        second_prompt_path=prompt2_file,
        model_id=MODEL_ID,
        time_taken=end_time - start_time,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        inter_out_path=first_output_md,
    )


# ──────────────────────────────
# Main pipeline
# ──────────────────────────────
def main(logs_file: Path, prompt1_file: Path, prompt2_file: Path, ts_temperature: float):
    """
    Analyze TS event logs:
    1. Split large logs JSON
    2. Generate timeline (first pass)
    3. Consolidate outputs
    4. Extract flagged events
    5. Generate flagged timeline (second pass)
    6. Token counting + append metadata
    """
    run_id = f"TS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = Path("./runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    setup_logging(run_dir)
    logging.info(f"Run started: {run_id}")

    start_time = time.time()

    # 1. Split logs
    if not logs_file.exists():
        logging.error(f"Logs file not found: {logs_file}")
        sys.exit(1)
    json_name, _, num_parts = split_logs(logs_file)

    # 2. First pass
    first_output_md = generate_first_pass(run_dir, prompt1_file, num_parts, json_name, ts_temperature)
    time.sleep(SLEEP_BETWEEN_STAGES)

    # 3. Consolidate
    combined_json = consolidate_outputs(run_dir)
    time.sleep(SLEEP_BETWEEN_STAGES)

    # 4. Extract flagged
    flagged_json = extract_flagged_events(run_dir, combined_json, logs_file)
    time.sleep(SLEEP_BETWEEN_STAGES)

    # 5. Second pass
    flagged_output_md = generate_second_pass(run_dir, prompt2_file, flagged_json, ts_temperature)
    time.sleep(SLEEP_BETWEEN_STAGES)

    # 6. Finalize
    finalize_results(
        flagged_output_md,
        first_output_md,
        prompt1_file,
        prompt2_file,
        json_name,
        run_dir,
        start_time,
    )

    logging.info(f"Analysis complete. Outputs saved in: {run_dir}")


# ──────────────────────────────
# Entry point
# ──────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze TS event logs and generate timelines.")
    parser.add_argument("logs_path", type=Path, help="Path to the uploaded TS logs file.")
    parser.add_argument("prompt1_path", type=Path, help="Path to the first prompt file.")
    parser.add_argument("prompt2_path", type=Path, help="Path to the second prompt file.")
    parser.add_argument("ts_temperature", type=float, help="Numeric parameter for TS processing (e.g., number of events).")
    args = parser.parse_args()

    main(args.logs_path, args.prompt1_path, args.prompt2_path, args.ts_temperature)

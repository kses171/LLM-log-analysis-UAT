#!/usr/bin/env python3
import json
import os
from dateutil import parser as dateparser
import tiktoken
from pathlib import Path


def split_json_by_tokens_and_time(
    input_file: Path,
    output_dir: Path,
    tokens_per_file: int = 50000,
    time_gap_seconds: int = 3600
):
    """
    Split a large JSON array into smaller parts based on token count and time gaps.
    
    Args:
        input_file: Path to the input JSON file containing an array of objects
        output_dir: Directory where the split parts will be written
        tokens_per_file: Maximum tokens per part (default: 50000)
        time_gap_seconds: Time gap in seconds to trigger a new part (default: 3600 = 1 hour)
    
    Returns:
        int: Number of parts created
    """
    def count_tokens(obj, encoder):
        """Return the number of tokens in the JSON serialization of obj."""
        text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
        return len(encoder.encode(text))

    def write_part(part_objs, part_index):
        """Write the list of objects to a JSON file."""
        os.makedirs(output_dir, exist_ok=True)
        out_path = output_dir / f"part_{part_index:02d}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(part_objs, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(part_objs)} objects to {out_path}")

    # Load all events
    with open(input_file, "r", encoding="utf-8") as f:
        events = json.load(f)

    # Prepare tokenizer
    encoder = tiktoken.get_encoding("cl100k_base")

    parts = []
    current_tokens = 0
    part_index = 1
    prev_time = None

    for ev in events:
        # Parse this event's time
        curr_time = dateparser.parse(ev["TimeCreated"])

        # How many tokens would this add?
        tok = count_tokens(ev, encoder)

        # Check size or time-gap thresholds
        exceed_token = (current_tokens + tok) > tokens_per_file
        exceed_time = (prev_time is not None and 
                      (curr_time - prev_time).total_seconds() > time_gap_seconds)

        if exceed_token or exceed_time:
            # Flush current part
            if parts:
                write_part(parts, part_index)
                part_index += 1

            # Start new part
            parts = [ev]
            current_tokens = tok
        else:
            # Append to current part
            parts.append(ev)
            current_tokens += tok

        prev_time = curr_time

    # Write any remaining
    if parts:
        write_part(parts, part_index)

    return part_index
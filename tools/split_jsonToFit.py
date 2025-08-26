#!/usr/bin/env python3
import json
import os
from datetime import datetime
from dateutil import parser as dateparser
import tiktoken

# Configuration
INPUT_FILE = "./runs/run38/flagged_detailed.json"      # big JSON file (an array of objects)
OUTPUT_DIR = "./requestsToLLM2/Tuesday-Filtered"       # where to write the parts
TOKENS_PER_FILE = 50000         # max tokens per part
TIME_GAP_SECONDS = 3600         # 1 hour

def count_tokens(obj, encoder):
    """Return the number of tokens in the JSON serialization of obj."""
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return len(encoder.encode(text))

def write_part(part_objs, part_index):
    """Write the list of objects to a JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"part_{part_index:02d}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(part_objs, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(part_objs)} objects to {out_path}")

def main():
    # load all events
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        events = json.load(f)

    # prepare tokenizer
    encoder = tiktoken.get_encoding("cl100k_base")

    parts = []
    current_tokens = 0
    part_index = 1
    prev_time = None

    for ev in events:
        # parse this event's time
        curr_time = dateparser.parse(ev["TimeCreated"])

        # how many tokens would this add?
        tok = count_tokens(ev, encoder)

        # check size or time-gap thresholds
        exceed_token = (current_tokens + tok) > TOKENS_PER_FILE
        exceed_time  = (prev_time is not None and 
                       (curr_time - prev_time).total_seconds() > TIME_GAP_SECONDS)

        if exceed_token or exceed_time:
            # flush current part
            if parts:
                write_part(parts, part_index)
                part_index += 1

            # start new part
            parts = [ev]
            current_tokens = tok
        else:
            # append to current part
            parts.append(ev)
            current_tokens += tok

        prev_time = curr_time

    # write any remaining
    if parts:
        write_part(parts, part_index)

if __name__ == "__main__":
    main()

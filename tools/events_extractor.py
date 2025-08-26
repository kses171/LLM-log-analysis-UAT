# events_extractor.py

import json
from pathlib import Path
from typing import Any, Dict, List, Union

def load_json(path: Path) -> Union[Dict[str, Any], List[Any]]:
    """
    Load and return JSON data from the given file path.
    """
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path: Path, data: Union[Dict[str, Any], List[Any]]) -> None:
    """
    Save the given data as pretty‑printed JSON to the given file path,
    creating parent directories if necessary.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_matches(
    flagged_json: Dict[str, Any],
    all_events: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Given a flagged JSON dict (with a "consolidated_flagged_records" list)
    and the full events list, return those events whose LineNumber appears
    among the flagged records.
    """
    record_numbers = {
        rec["LineNumber"]
        for rec in flagged_json.get("consolidated_flagged_records", [])
        if "LineNumber" in rec
    }

    matched: List[Dict[str, Any]] = []
    for evt in all_events:
        raw = evt.get("LineNumber")
        try:
            rn = int(raw)
        except (TypeError, ValueError):
            continue

        if rn in record_numbers:
            matched.append(evt)

    return matched

def extract_events(
    flagged_file: Union[str, Path],
    og_json_path: Union[str, Path],
    output_file: Union[str, Path]
) -> None:
    """
    Load `og_json_path` (the master events list) and `flagged_file` (which
    must contain a "consolidated_flagged_records" list with LineNumber fields),
    extract matching events, sort them by their "TimeCreated" field, and
    write the result to `output_file`.
    """
    flagged_file = Path(flagged_file)
    og_json_path = Path(og_json_path)
    output_file = Path(output_file)

    # 1. Load all events
    all_events = load_json(og_json_path)

    # 2. Load flagged records and extract matches
    flagged = load_json(flagged_file)
    matches = extract_matches(flagged, all_events)
    print(f"[{flagged_file.name}] → {len(matches)} matched records")

    # 3. Sort matches by timestamp
    #sorted_matches = sorted(matches, key=lambda e: e.get("TimeCreated"))
    sorted_matches = matches
    # 4. Save
    save_json(output_file, sorted_matches)
    print(f"Total matched events: {len(sorted_matches)}")
    print(f"Wrote results to {output_file}")


if __name__ == "__main__":
    # === CONFIGURE THESE PATHS ===
    FLAGGED_FILE  = Path("./runs/run9/combined.json")
    OG_JSON_PATH  = Path("./json_data2/mediumCSV-2.json")
    OUTPUT_FILE   = Path("./runs/run9/flagged_detailed.json")
    # ============================

    extract_events(FLAGGED_FILE, OG_JSON_PATH, OUTPUT_FILE)

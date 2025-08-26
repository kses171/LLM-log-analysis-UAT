#!/usr/bin/env python3
# md_flag_consolidator.py

import re
import json
from pathlib import Path
from typing import List, Dict, Union

def extract_flagged_from_md(md_text: str) -> List[Dict[str, Union[int, str]]]:
    """
    Find all JSON-like records in the markdown text and
    return a list of dicts where each has keys:
      - LineNumber (int)
      - Summary (str)
      - reason  (str)
    """
    record_pattern = re.compile(
        r"""\{
            \s*"LineNumber"\s*:\s*(?P<LineNumber>\d+)\s*,      # line number
            \s*"Summary"\s*:\s*"(?P<Summary>(?:\\.|[^"\\])*)"\s*,  # summary (handles escapes)
            \s*"[Rr]eason"\s*:\s*"(?P<reason>(?:\\.|[^"\\])*)"\s*    # reason
        \}""",
        re.VERBOSE | re.DOTALL
    )

    flagged = []
    for match in record_pattern.finditer(md_text):
        rec = {
            "LineNumber": int(match.group("LineNumber")),
            "Summary":    match.group("Summary"),
            "reason":     match.group("reason")
        }
        flagged.append(rec)
    return flagged

def consolidate(
    input_dir: Union[str, Path],
    output_file: Union[str, Path],
    annotate_source: bool = True
) -> None:
    """
    Walks `input_dir` (recursively), reads every .md file, extracts flagged records,
    and writes them into a single JSON at `output_file` with this structure:
    
    {
      "consolidated_flagged_records": [ ... ],
      "total_flagged": <count>
    }
    
    If annotate_source is True, each record gets a "source_file" key.
    """
    input_path = Path(input_dir)
    if not input_path.is_dir():
        raise ValueError(f"Input path {input_dir} is not a directory")

    all_flagged = []
    for md_file in input_path.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        records = extract_flagged_from_md(text)
        if records and annotate_source:
            for rec in records:
                rec["source_file"] = str(md_file)
        all_flagged.extend(records)

    output_data = {
        "consolidated_flagged_records": all_flagged,
        "total_flagged": len(all_flagged)
    }

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(all_flagged)} records to {output_file}")

if __name__ == "__main__":
    # === CONFIGURE THESE PATHS ===
    LOG_NAME    = "TS"
    INPUT_DIR   = Path(f"./rawOutputLLM2/{LOG_NAME}")
    OUTPUT_FILE = Path(f"./rawOutputLLM2/Consolidated/{LOG_NAME}-combined.json")
    # ============================

    consolidate(INPUT_DIR, OUTPUT_FILE)

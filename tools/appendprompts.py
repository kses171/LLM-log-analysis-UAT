from pathlib import Path

def append_prompts_to_md(md_filepath: Path, first_prompt_path: Path, \
                         second_prompt_path: Path, model_id : str, \
                         time_taken: int, input_tokens: int, output_tokens: int, inter_out_path: Path) -> None:
    """
    Append structured prompts to a Markdown file.

    The following will be appended in order:
      1. "# Prompts" heading
      2. "# 1st prompt" heading
      3. Contents of first_prompt_path
      4. "# 2nd prompt" heading
      5. Contents of second_prompt_path
      6. Contents of inter_out_path

    If the Markdown file does not exist, it will be created.

    Args:
        md_filepath: Path to the Markdown file to append to.
        first_prompt_path: Path to the first prompt text file.
        second_prompt_path: Path to the second prompt text file.
        model_id: Model ID (e.g 'us.meta.llama3-3-70b-instruct-v1:0') used.
        time_taken:
        input_tokens:
        output_tokens:

    Raises:
        FileNotFoundError: If either prompt file does not exist.
        OSError: For other file I/O errors.
    """
    # Coerce to Path objects
    md_filepath = Path(md_filepath)
    first_prompt_path = Path(first_prompt_path)
    second_prompt_path = Path(second_prompt_path)
    third_path = Path(inter_out_path)
    
    # Ensure prompt files exist
    for p in (first_prompt_path, second_prompt_path):
        if not p.is_file():
            raise FileNotFoundError(f"Prompt file not found: {p}")

    # Read prompt contents
    first_content = first_prompt_path.read_text(encoding='utf-8')
    second_content = second_prompt_path.read_text(encoding='utf-8')

    # Intermediate output
    third_content = third_path.read_text(encoding='utf-8')

    # Build the section to append
    section = (
        "\n# Prompts\n\n"
        "### Model ID\n\n"
        f"{model_id.rstrip()}\n\n"
        "### Metrics\n\n"
        f"Time taken: {time_taken:.4f}\n\n"
        f"Output tokens: {output_tokens}\n\n"
        f"Input tokens: {input_tokens}\n\n"
        "### 1st prompt\n\n"
        "```md\n"
        f"{first_content.replace('`', '').rstrip()}\n\n"
        "```\n"
        "### 2nd prompt\n\n"
        "```md\n"
        f"{second_content.replace('`', '').rstrip()}\n"
        "```\n"
        "# Intermediate Output\n\n"
        f"{third_content.replace('`', '').rstrip()}\n"
    )

    # Append to the markdown file
    with md_filepath.open('a', encoding='utf-8') as md_file:
        md_file.write(section)

if __name__ == "__main__":
    # === CONFIGURE THESE PATHS AND PARAMETERS ===
    MD_FILEPATH        = "./runs/run6/final.md"
    FIRST_PROMPT_PATH  = "./prompts2/TS3.txt"
    SECOND_PROMPT_PATH = "./prompts2/TS-all-4.txt"
    MODEL_ID           = "us.meta.llama3-3-70b-instruct-v1:0"
    # ============================================

    append_prompts_to_md(MD_FILEPATH, FIRST_PROMPT_PATH, SECOND_PROMPT_PATH, MODEL_ID)
import tiktoken
import json
import sys
from pathlib import Path

def count_tokens_from_file(file_path, model="gpt-4"):
    """
    Count tokens in a file using tiktoken
    
    Args:
        file_path (str): Path to the file
        model (str): Model name for tokenizer (e.g., 'gpt-4', 'gpt-3.5-turbo', 'cl100k_base')
    
    Returns:
        int: Number of tokens
    """
    try:
        # Get the encoding for the specified model
        encoding = tiktoken.encoding_for_model(model)
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Count tokens
        tokens = encoding.encode(content)
        return len(tokens)
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except UnicodeDecodeError:
        print(f"Error: Could not decode file '{file_path}'. Try a different encoding.")
        return None
    except KeyError:
        print(f"Error: Model '{model}' not recognized. Try 'gpt-4', 'gpt-3.5-turbo', or 'cl100k_base'.")
        return None
    

def count_output_tokens(base_runs_dir: Path, run_id: str):
    run_dir = base_runs_dir / run_id
    path1 = run_dir / f"{run_id}-1.md"
    path2 = run_dir / f"{run_id}-2.md"
    return count_tokens_from_file(path1) + count_tokens_from_file(path2)
    #return count_tokens_from_file(path2)

def count_input_tokens(prompt1_path: Path, prompt2_path: Path, requests_folder: Path):
    json_tokens, total_jsons = 0, 0  # Initialize both variables properly
    for file in requests_folder.iterdir():
        if file.is_file():  # Only process files, not subdirectories
            json_tokens += count_tokens_from_file(file)  # Use correct function name
            total_jsons += 1
    prompts_token1 = count_tokens_from_file(prompt1_path) * total_jsons
    prompts_token2 = count_tokens_from_file(prompt2_path)
    #prompts_token1 = count_tokens_from_file(prompt1_path) * total_jsons
    return prompts_token1 + json_tokens + prompts_token2 # Include json_tokens in return value


#print(count_output_tokens(Path("./runs"), 'run11'))
prompts_dir = Path("./prompts2")
prompt_file1 = prompts_dir / 'TS3.txt'
prompt_file2 = prompts_dir / 'TS-all-4.txt'
json_path = Path('./requestsToLLM2/TS/')
#print(count_input_tokens(prompt_file1, prompt_file2, json_path))

import os
import csv
import random
from difflib import unified_diff
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from huggingface_hub import login
import torch
from tqdm import tqdm

load_dotenv()
login()

# Load HF model
model_id = "mistralai/Mistral-7B-Instruct-v0.3"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

def ask_local_model(prompt):
    response = pipe(prompt, max_new_tokens=64, do_sample=False)
    return response[0]['generated_text'].split(prompt)[-1].strip()

# Directories
ORIGINAL_DIR = "original_musicxml"
ROUNDTRIPPED_DIR = "roundtrip_musicxml"
RESULT_CSV = "semantic_gpt_comparison_results.csv"
MAX_FILES = 500

def summarize_diff(original_text, new_text):
    """Return a compact unified diff string."""
    diff = list(unified_diff(
        original_text.splitlines(),
        new_text.splitlines(),
        lineterm='',
        n=3
    ))
    return '\n'.join(diff[:100])  # Trim long diffs

def check_if_equivalent(diff):
    prompt = f"""
The following is a diff between two MusicXML files — the original and a round-tripped version.
Please answer if they are semantically equivalent (e.g., they represent the same music).
Only answer "Yes" or "No", followed optionally by a 1-sentence explanation.

Diff:
{diff}
"""
    return ask_local_model(prompt)

def normalize_key(f):
    return f.replace("_roundtrip", "").replace(".musicxml", "")

def run_comparison():
    # Map: normalized key → full real filename
    original_files = {
        normalize_key(f): f
        for f in os.listdir(ORIGINAL_DIR)
        if f.endswith(".musicxml")
    }

    roundtrip_files = {
        normalize_key(f): f
        for f in os.listdir(ROUNDTRIPPED_DIR)
        if f.endswith(".musicxml")
    }

    shared_keys = list(set(original_files.keys()) & set(roundtrip_files.keys()))
    print(f"✅ Found {len(shared_keys)} matched MusicXML file pairs.")

    if MAX_FILES:
        shared_keys = random.sample(shared_keys, min(MAX_FILES, len(shared_keys)))

    results = []

    for key in tqdm(shared_keys, desc="🔍 Comparing files"):
        original_path = os.path.join(ORIGINAL_DIR, original_files[key])
        roundtrip_path = os.path.join(ROUNDTRIPPED_DIR, roundtrip_files[key])

        try:
            with open(original_path, 'r') as f1, open(roundtrip_path, 'r') as f2:
                original_text = f1.read()
                roundtrip_text = f2.read()

            diff_snippet = summarize_diff(original_text, roundtrip_text)
            verdict = check_if_equivalent(diff_snippet)

            results.append((original_files[key], verdict, diff_snippet))
            print(f"{original_files[key]}: {verdict}")
        except Exception as e:
            results.append((original_files[key], f"Error: {e}", "N/A"))
            print(f"{original_files[key]}: Error - {e}")

    with open(RESULT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "LLM Verdict", "Diff Snippet"])
        writer.writerows(results)

if __name__ == "__main__":
    run_comparison()

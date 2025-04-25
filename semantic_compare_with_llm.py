import os
import csv
import random
import openai
from difflib import unified_dif
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Directories
ORIGINAL_DIR = "original_musicxml"
ROUNDTRIPPED_DIR = "roundtripped_musicxml"
RESULT_CSV = "semantic_gpt_comparison_results.csv"

# Optional: limit number of comparisons (e.g., 500 max to control cost)
MAX_FILES = 500


def summarize_diff(original_text, new_text):
    """Return a compact unified diff string."""
    diff = list(
        unified_diff(
            original_text.splitlines(),
            new_text.splitlines(),
            lineterm='',
            n=3  # show 3 lines of context
        ))
    return '\n'.join(diff[:100])  # limit for token size


def ask_gpt_if_equivalent(original_text, new_text):
    diff = summarize_diff(original_text, new_text)

    prompt = f"""
The following is a diff between two MusicXML files — the original and a round-tripped version.
Please answer if they are semantically equivalent (e.g., they represent the same music).
Only answer "Yes" or "No", followed optionally by a 1-sentence explanation.

Diff:
{diff}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",  # Or "gpt-3.5-turbo" if on budget
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0,
        max_tokens=50,
    )

    return response['choices'][0]['message']['content'].strip()


def run_comparison():
    all_files = os.listdir(ORIGINAL_DIR)
    all_files = [f for f in all_files if f.endswith('.musicxml')]

    if MAX_FILES:
        all_files = random.sample(all_files, min(MAX_FILES, len(all_files)))

    results = []

    for filename in all_files:
        original_path = os.path.join(ORIGINAL_DIR, filename)
        roundtrip_path = os.path.join(ROUNDTRIPPED_DIR, filename)

        if not os.path.exists(roundtrip_path):
            results.append((filename, "Missing roundtrip file"))
            continue

        with open(original_path, 'r') as f1, open(roundtrip_path, 'r') as f2:
            original_text = f1.read()
            roundtrip_text = f2.read()

        verdict = ask_gpt_if_equivalent(original_text, roundtrip_text)
        results.append((filename, verdict))

        print(f"{filename}: {verdict}")

    with open(RESULT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "GPT Verdict"])
        writer.writerows(results)


if __name__ == "__main__":
    run_comparison()

import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

#####################################################################
# Converts **kern tokens to **ekern, handling compound tokens
#####################################################################

def kern_to_ekern(token):
    ekern_tokens = []

    # Handle leading grace or tuplet markers like '(' or ')'
    while token and token[0] in '(){}[]':
        ekern_tokens.append(token[0])
        token = token[1:]

    # Duration (e.g., 4, 8., 16..)
    duration_match = re.match(r'\d+\.*', token)
    if duration_match:
        ekern_tokens.append(duration_match.group(0))
        token = token[len(duration_match.group(0)):]  # remove from token

    # Pitch letter (A-G or a-g)
    pitch_match = re.match(r'[A-Ga-g]+', token)
    if pitch_match:
        ekern_tokens.append(pitch_match.group(0))
        token = token[len(pitch_match.group(0)):]  # remove from token

    # Accidentals (e.g., #, -, n)
    while token and token[0] in '#-n':
        ekern_tokens.append(token[0])
        token = token[1:]

    # Articulations and other suffix symbols (., >, etc.)
    for char in token:
        ekern_tokens.append(char)

    return '·'.join(ekern_tokens)

def clean_kern(krn_lines):
    avoid_tokens = [
        '*Xped', '*staff1', '*staff2', '*tremolo', '*ped', '*Xtuplet', '*tuplet',
        '*Xtremolo', '*cue', '*Xcue', '*rscale:1/2', '*rscale:1', '*kcancel', '*below',
        '*IC:', '*IG:', '*IN:', '*ITr:', '*IT:', '*YOP', '*YOX'
    ]
    cleaned = []
    for line in krn_lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("!"):
            continue
        if any(tok in line for tok in avoid_tokens):
            continue
        cleaned.append(line)
    return cleaned

def convert_kern_file_to_ekern(input_output_paths):
    input_path, output_path = input_output_paths
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()

        music_lines = clean_kern(lines)
        ekern_output = []

        for line in music_lines:
            converted_line = []
            for token in line.split('\t'):
                if token.strip():
                    converted_line.append(kern_to_ekern(token.strip()))
            ekern_output.append(" ".join(converted_line))

        with open(output_path, 'w') as f:
            f.write("\n".join(ekern_output))
        return f"Converted: {input_path} → {output_path}"
    except Exception as e:
        return f"Error converting {input_path}: {e}"

def batch_convert(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    tasks = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".krn"):
            in_path = os.path.join(input_dir, filename)
            out_path = os.path.join(output_dir, filename.replace(".krn", ".ekern"))
            tasks.append((in_path, out_path))

    with ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(convert_kern_file_to_ekern, tasks), total=len(tasks)))

    for res in results:
        print(res)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python convert_to_ekern.py <input_kern_dir> <output_ekern_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    batch_convert(input_dir, output_dir)

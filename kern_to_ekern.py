
import os
import re

#####################################################################
# converts kern to ekern
#####################################################################

def kern_to_ekern(token):
    ekern_tokens = []

    duration_match = re.match(r'^(\d+\.?)+', token)
    if duration_match:
        ekern_tokens.append(duration_match.group(0))
        token = token[len(duration_match.group(0)):]

    pitch_match = re.match(r'[A-Ga-g]+', token)
    if pitch_match:
        ekern_tokens.append(pitch_match.group(0))
        token = token[len(pitch_match.group(0)):]

    while token and token[0] in '#-n':
        ekern_tokens.append(token[0])
        token = token[1:]

    for char in token:
        ekern_tokens.append(char)

    return '·'.join(ekern_tokens)

def clean_kern(krn_lines):
    avoid_tokens = [
        '*Xped', '*staff1', '*staff2', '*tremolo', '*ped', '*Xtuplet', '*tuplet',
        '*Xtremolo', '*cue', '*Xcue', '*rscale:1/2', '*rscale:1', '*kcancel', '*below'
    ]
    cleaned = []
    for line in krn_lines:
        if line.startswith("*") or line.startswith("=") or any(tok in line for tok in avoid_tokens):
            continue
        cleaned.append(line.strip())
    return cleaned

def convert_kern_file_to_ekern(input_path, output_path):
    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    music_lines = clean_kern(lines)
    ekern_output = []

    for line in music_lines:
        for token in line.split('\t'):
            if token.strip():
                ekern_output.append(kern_to_ekern(token.strip()))

    with open(output_path, 'w') as f:
        f.write(" ".join(ekern_output))
    print(f"Converted: {input_path} → {output_path}")

def batch_convert(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith(".krn"):
            in_path = os.path.join(input_dir, filename)
            out_path = os.path.join(output_dir, filename.replace(".krn", ".ekern"))
            convert_kern_file_to_ekern(in_path, out_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python convert_to_ekern.py <input_kern_dir> <output_ekern_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    batch_convert(input_dir, output_dir)

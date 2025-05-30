import os
import sys
import re

#####################################################################
# old file that converts kern to bekern (no longer needed)
#####################################################################

def clean_kern(krn,
               avoid_tokens=[
                   '*Xped', '*staff1', '*staff2', '*tremolo', '*ped',
                   '*Xtuplet', '*tuplet', "*Xtremolo", '*cue', '*Xcue',
                   '*rscale:1/2', '*rscale:1', '*kcancel', '*below'
               ]):
    krn = krn.split('\n')
    newkrn = []
    for idx, line in enumerate(krn):
        if not any([token in line.split('\t') for token in avoid_tokens]):
            if not all([token == '*' for token in line.split('\t')]):
                newkrn.append(line.replace("\n", ""))
    return "\n".join(newkrn)


def parse_kern(krn: str) -> str:
    krn = clean_kern(krn)
    krn = krn.replace(" ", " <s> ")
    krn = krn.replace("\t", " <t> ")
    krn = krn.replace("\n", " <b> ")
    krn = krn.replace("·/", "")
    krn = krn.replace("·\\", "")
    krn = krn.split(" ")[4:]
    krn = [re.sub(r'(?<=\=)\d+', '', token) for token in krn]
    return " ".join(krn)


def convert_kern_to_bekern(kern_file_path, bekern_file_path):
    try:
        with open(kern_file_path, "r") as f:
            kern_data = f.read()
        bekern_data = parse_kern(kern_data)
        with open(bekern_file_path, "w") as f:
            f.write(bekern_data)
        print(f"Converted: {kern_file_path} -> {bekern_file_path}")
    except FileNotFoundError:
        print(f"Error: Kern file not found at {kern_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_to_bekern.py <input_kern_directory>")
        sys.exit(1)

    input_kern_dir = sys.argv[1]
    output_bekern_dir = "bekern_output"  
    os.makedirs(output_bekern_dir,
                exist_ok=True)  

    for filename in os.listdir(input_kern_dir):
        if filename.endswith(".krn"):
            input_kern_file = os.path.join(input_kern_dir, filename)
            output_bekern_file = os.path.join(
                output_bekern_dir, filename.replace(".krn", ".bekern"))
            convert_kern_to_bekern(input_kern_file, output_bekern_file)

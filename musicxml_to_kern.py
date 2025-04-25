import os
import subprocess
from pathlib import Path

synthetic_dir = Path("./olimpic-1.0-synthetic/samples")
scanned_dir = Path("./olimpic-1.0-scanned/samples")
output_dir = Path("./converted_kern")
output_dir.mkdir(parents=True, exist_ok=True)


def convert_musicxml_to_kern(input_file, output_file):
    """Converts a MusicXML file to Humdrum/Kern using musicxml2hum."""
    try:
        print(f"Processing {input_file}")
        subprocess.run(
            ["musicxml2hum", str(input_file)],
            capture_output=True,
            text=True,
            check=True,
        )

        result = subprocess.run(
            ["musicxml2hum", str(input_file)],
            capture_output=True,
            text=True,
            check=True,
        )

        with open(output_file, "w") as f:
            f.write(result.stdout)

        print(f"Converted: {input_file} -> {output_file.name}")

    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")
    except FileNotFoundError:
        print(
            "musicxml2hum command not found. Please ensure it is installed and in your PATH."
        )


for root_dir in [synthetic_dir, scanned_dir]:
    for sample_id_folder in root_dir.iterdir():
        if not sample_id_folder.is_dir():
            continue

        for musicxml_file in sample_id_folder.glob("*.musicxml"):
            output_file = (output_dir /
                           f"{sample_id_folder.name}_{musicxml_file.stem}.krn")
            convert_musicxml_to_kern(musicxml_file, output_file)

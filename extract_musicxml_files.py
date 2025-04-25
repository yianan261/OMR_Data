import os
from pathlib import Path
import shutil

synthetic_dir = Path("./olimpic-1.0-synthetic/samples")
scanned_dir = Path("./olimpic-1.0-scanned/samples")

# Output directory for comparison
output_dir = Path("./original_musicxml")
output_dir.mkdir(parents=True, exist_ok=True)

for root_dir in [synthetic_dir, scanned_dir]:
    for sample_folder in root_dir.iterdir():
        if not sample_folder.is_dir():
            continue

        for musicxml_file in sample_folder.glob("*.musicxml"):
            new_filename = f"{sample_folder.name}_{musicxml_file.name}"
            destination = output_dir / new_filename

            try:
                shutil.copy2(musicxml_file, destination)
                print(f"Copied {musicxml_file} -> {destination.name}")
            except Exception as e:
                print(f"Failed to copy {musicxml_file}: {e}")

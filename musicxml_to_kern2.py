import os
import subprocess
from pathlib import Path
import csv

synthetic_dir = Path("./olimpic-1.0-synthetic/samples")
scanned_dir = Path("./olimpic-1.0-scanned/samples")
output_dir = Path("./converted_kern2")
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
        return True  # Indicate successful conversion
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")
        return False  # Indicate failed conversion
    except FileNotFoundError:
        print(
            "musicxml2hum command not found. Please ensure it is installed and in your PATH."
        )
        return False  # Indicate failed conversion


if __name__ == "__main__":
    processed_files = []
    failed_files = []

    with open("converted_files.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Original MusicXML File", "Converted Kern File", "Status"])

        for root_dir in [synthetic_dir, scanned_dir]:
            print(f"Processing root directory: {root_dir}")
            for sample_id_folder in root_dir.iterdir():
                print(f"  Processing sample ID folder: {sample_id_folder}")
                if not sample_id_folder.is_dir():
                    print(f"    Skipping non-directory: {sample_id_folder}")
                    continue

                for musicxml_file in sample_id_folder.glob("*.musicxml"):
                    print(f"    Found MusicXML file: {musicxml_file}")
                    output_file = (
                        output_dir /
                        f"{sample_id_folder.name}_{musicxml_file.stem}.krn")
                    conversion_successful = convert_musicxml_to_kern(
                        musicxml_file, output_file)
                    if conversion_successful:
                        processed_files.append(str(musicxml_file))
                        writer.writerow(
                            [str(musicxml_file),
                             str(output_file), "Success"])
                    else:
                        failed_files.append(str(musicxml_file))
                        writer.writerow(
                            [str(musicxml_file),
                             str(output_file), "Failure"])

    print("\nConversion Summary:")
    print(
        f"  Total processed files: {len(processed_files) + len(failed_files)}")
    print(f"  Successfully converted: {len(processed_files)}")
    print(f"  Failed conversions: {len(failed_files)}")

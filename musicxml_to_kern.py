import os
import subprocess
from pathlib import Path
import csv
import argparse
import zipfile

synthetic_dir = Path("./olimpic-1.0-synthetic/samples")
scanned_dir = Path("./olimpic-1.0-scanned/samples")
output_dir = Path("./converted_kern2")
pdmx_dir = Path("./mxl/")
pdmx_output_dir = Path("./pdmx_to_kern")
pdmx_output_dir.mkdir(parents=True,exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)

def extract_mxl(mxl_path, output_dir):
    with zipfile.ZipFile(mxl_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

def convert_musicxml_to_kern(input_file, output_file):
    """Converts a MusicXML file to Humdrum/Kern using musicxml2hum."""
    try:
        print(f"Processing {input_file}")

        result = subprocess.run(
            ["musicxml2hum", str(input_file)],
            capture_output=True,
            text=True,
            check=True,
        )

        with open(output_file, "w") as f:
            f.write(result.stdout)

        print(f"Converted: {input_file} -> {output_file.name}")
        return True  
    except subprocess.CalledProcessError as e:
        print(f"Trying to unzip and re-run for {input_file}")
        file_stem = input_file.stem
        temp_dir = Path("./extracted_pdmx_xml")
        temp_dir.mkdir(exist_ok=True)
        extract_path = temp_dir / file_stem
        try:
            with zipfile.ZipFile(input_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            score_path = temp_dir / "score.xml"
            if score_path.exists():
                return convert_musicxml_to_kern(score_path, output_file)
        except Exception as e:
            print(f"Unzipping failed: {e}")
        return False 
    except FileNotFoundError:
        print(
            "musicxml2hum command not found. Please ensure it is installed and in your PATH."
        )
        return False  
# olimpic dataset
def process_directory(input_root_dirs, output_dir, csv_writer):
    processed_files = []
    failed_files = []

    for root_dir in input_root_dirs:
        print(f"Processing root directory: {root_dir}")
        for sample_id_folder in root_dir.iterdir():
            print(f"  Processing sample ID folder: {sample_id_folder}")
            if not sample_id_folder.is_dir():
                print(f"    Skipping non-directory: {sample_id_folder}")
                continue

            for musicxml_file in sample_id_folder.glob("*.musicxml"):
                print(f"    Found MusicXML file: {musicxml_file}")
                output_file = output_dir / f"{sample_id_folder.name}_{musicxml_file.stem}.krn"
                success = convert_musicxml_to_kern(musicxml_file, output_file)

                if success:
                    processed_files.append(str(musicxml_file))
                    csv_writer.writerow([str(musicxml_file), str(output_file), "Success"])
                else:
                    failed_files.append(str(musicxml_file))
                    csv_writer.writerow([str(musicxml_file), str(output_file), "Failure"])

    return processed_files, failed_files

def process_pdmx(csv_writer):
    processed_files = []
    failed_files = []

    for subdir in pdmx_dir.iterdir():
        for ssubdir in subdir.iterdir():
            for musicxml_file in ssubdir.glob("*.xml"):
                print(f"Found PDMX file: {musicxml_file}")
                output_file = pdmx_output_dir / f"{musicxml_file.stem}.krn"
                success = convert_musicxml_to_kern(musicxml_file, output_file)

                if success:
                    processed_files.append(str(musicxml_file))
                    csv_writer.writerow([str(musicxml_file), str(output_file), "Success"])
                else:
                    failed_files.append(str(musicxml_file))
                    csv_writer.writerow([str(musicxml_file), str(output_file), "Failure"])

    return processed_files, failed_files
                

def main():
    parser = argparse.ArgumentParser(description="Convert MusicXML to Humdrum/Kern")
    parser.add_argument("dataset", choices=["olimpic", "pdmx"], help="Choose dataset to convert")
    args = parser.parse_args()

    with open("converted_files.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original MusicXML file", "Converted Kern File", "Status"])

        if args.dataset == "olimpic":
            processed, failed = process_directory([synthetic_dir, scanned_dir], output_dir, writer)
        elif args.dataset == "pdmx":
            processed, failed = process_pdmx(writer)
        else:
            raise ValueError("Unsupported dataset argument.")

    print("\nConversion Summary:")
    print(f"  Total processed files: {len(processed) + len(failed)}")
    print(f"  Successfully converted: {len(processed)}")
    print(f"  Failed conversions: {len(failed)}")

if __name__ == "__main__":
    main()
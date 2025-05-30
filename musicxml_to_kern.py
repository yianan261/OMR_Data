import os
import subprocess
from pathlib import Path
import csv
import argparse
import zipfile

##############################################################################
# converts musicxml datasets (olimpic and pdmx)to kern
# make sure you have humlib installed in your environment to use musicxml2hum
# make sure you have the olimpic datasets directory in the same level
# the olimpic datasets has 2 sets, the synthetic and scanned samples
# make sure you have the pdmx datasets directory in the same level
# check synthetic_dir, scanned_dir, pdmx_dir for directory path names
# run 'python musicxml_to_kern.py olimpic' to convert olimpic datasets
# run 'python musicxml_to_kern.py pdmx' to convert pdmx datasets
##############################################################################

synthetic_dir = Path("./olimpic-1.0-synthetic/samples")
scanned_dir = Path("./olimpic-1.0-scanned/samples")
output_dir = Path("./converted_kern2")
pdmx_dir = Path("./mxl/")
pdmx_output_dir = Path("./pdmx_to_kern")
extracted_pdmx_dir = Path("./extracted_pdmx_xml")

pdmx_output_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)
extracted_pdmx_dir.mkdir(parents=True, exist_ok=True)

os.environ["PATH"] = "/home/aisec/humlib/bin:" + os.environ["PATH"]

def extract_all_pdmx(skip_existing=True):
    for subdir in pdmx_dir.iterdir():
        for ssubdir in subdir.iterdir():
            for mxl_file in ssubdir.glob("*.mxl"):
                file_id = mxl_file.stem
                extract_path = extracted_pdmx_dir / file_id
                
                if skip_existing and extract_path.exists() and any(extract_path.glob("*.xml")):
                    print(f"Skipping already extracted: {file_id}")
                    continue

                extract_path.mkdir(parents=True, exist_ok=True)
                try:
                    with zipfile.ZipFile(mxl_file, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
                    print(f"Extracted: {mxl_file} -> {extract_path}")
                except Exception as e:
                    print(f"Failed to extract {mxl_file}: {e}")

def convert_musicxml_to_kern(input_file, output_file):
    try:
        print(f"Processing {input_file}")

        result = subprocess.run(
            ["musicxml2hum", str(input_file)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.stdout.strip():
            with open(output_file, "w") as f:
                f.write(result.stdout)
            print(f"Converted: {input_file} → {output_file.name}")
            return True
        else:
            print(f"Skipped writing empty output for {input_file}")
            print(f"stderr: {result.stderr.strip()[:300]}")
            return False

    except FileNotFoundError:
        print("musicxml2hum command not found. Please ensure it is installed and in your PATH.")
        return False

def process_extracted_pdmx(csv_writer):
    processed_files = []
    failed_files = []

    for file_id_dir in extracted_pdmx_dir.iterdir():
        if not file_id_dir.is_dir():
            continue

        xml_files = list(file_id_dir.glob("*.xml"))
        if not xml_files:
            print(f"No .xml found in {file_id_dir}")
            continue

        xml_file = xml_files[0]
        output_file = pdmx_output_dir / f"{xml_file.stem}.krn"
        success = convert_musicxml_to_kern(xml_file, output_file)

        if success:
            processed_files.append(str(xml_file))
            csv_writer.writerow([str(xml_file), str(output_file), "Success"])
        else:
            failed_files.append(str(xml_file))
            csv_writer.writerow([str(xml_file), str(output_file), "Failure"])

    return processed_files, failed_files

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

def main():
    parser = argparse.ArgumentParser(description="Convert MusicXML to Humdrum/Kern")
    parser.add_argument("dataset", choices=["olimpic", "pdmx"], help="Choose dataset to convert")
    parser.add_argument("--reextract", action="store_true", help="Force re-extraction of all PDMX MXL files")
    args = parser.parse_args()

    with open("converted_files.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original MusicXML file", "Converted Kern File", "Status"])

        if args.dataset == "olimpic":
            processed, failed = process_directory([synthetic_dir, scanned_dir], output_dir, writer)
        elif args.dataset == "pdmx":
            extract_all_pdmx(skip_existing=not args.reextract)
            processed, failed = process_extracted_pdmx(writer)
        else:
            raise ValueError("Unsupported dataset argument.")

    print("\nConversion Summary:")
    print(f"  Total processed files: {len(processed) + len(failed)}")
    print(f"  Successfully converted: {len(processed)}")
    print(f"  Failed conversions: {len(failed)}")

if __name__ == "__main__":
    main()
import os
import subprocess
from pathlib import Path
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

# Paths
extracted_pdmx_dir = Path("./extracted_pdmx_xml")
pdmx_output_dir = Path("./pdmx_to_kern")
pdmx_output_dir.mkdir(parents=True, exist_ok=True)

os.environ["PATH"] = "/home/aisec/humlib/bin:" + os.environ["PATH"]

def convert_musicxml_to_kern_task(xml_file, krn_file):
    if krn_file.exists() and os.path.getsize(krn_file) > 10:
        return (str(xml_file), str(krn_file), "Skipped")

    try:
        result = subprocess.run(
            ["musicxml2hum", str(xml_file)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.stdout.strip():
            with open(krn_file, "w") as f:
                f.write(result.stdout)
            return (str(xml_file), str(krn_file), "Success")
        else:
            return (str(xml_file), str(krn_file), "Failure")
    except Exception as e:
        return (str(xml_file), str(krn_file), "Failure")

def rerun_conversion_parallel(num_workers=None):
    tasks = []

    for subdir in extracted_pdmx_dir.iterdir():
        if not subdir.is_dir():
            continue
        xml_files = list(subdir.glob("*.xml"))
        if not xml_files:
            continue

        xml_file = xml_files[0]
        krn_file = pdmx_output_dir / f"{xml_file.stem}.krn"
        tasks.append((xml_file, krn_file))

    successes, failures, skipped = 0, 0, 0
    with open("rerun_converted_files.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["XML File", "Kern File", "Status"])

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(convert_musicxml_to_kern_task, xml, krn) for xml, krn in tasks]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Converting files"):
                xml_file, krn_file, status = future.result()
                writer.writerow([xml_file, krn_file, status])
                if status == "Success":
                    successes += 1
                elif status == "Failure":
                    failures += 1
                else:
                    skipped += 1

    print("\n Done.")
    print(f"   Successfully converted: {successes}")
    print(f"   Failed conversions: {failures}")
    print(f"   Skipped files: {skipped}")

if __name__ == "__main__":
    rerun_conversion_parallel(num_workers=None)  

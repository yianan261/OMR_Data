import os
from pathlib import Path
import filecmp
import csv

#####################################################################
# file that compares the transcribed xml file from kern file to original 
# xml file (checking hum2musicxml correctness)
#####################################################################

def export_filenames(directories, output_file):
    """
    Exports the filenames from the given directories to the specified output file.

    Args:
        directories: A list of directories to scan for .musicxml files.
        output_file: The path to the output text file.
    """
    filenames = []
    for directory in directories:
        for item in Path(directory).iterdir():
            if item.is_dir():
                for file_path in item.glob("*.musicxml"):
                    filenames.append(f"{item.name}_{file_path.stem}.musicxml")
    with open(output_file, "w") as f:
        for name in sorted(filenames):
            f.write(name + "\n")
    print(f"Filenames from {directories} exported to {output_file}")


def export_roundtrip_filenames(directory, output_file):
    """
    Exports the filenames from the roundtrip directory to the specified output file.

    Args:
        directory: The directory to scan for *_roundtrip.musicxml files.
        output_file: The path to the output text file.
    """
    filenames = []
    for file_path in Path(directory).glob("*_roundtrip.musicxml"):
        save_path_name = file_path.stem.replace("_roundtrip", "")
        filenames.append(save_path_name)
    with open(output_file, "w") as f:
        for name in sorted(filenames):
            f.write(name + "\n")
    print(f"Filenames from {directory} exported to {output_file}")


def compare_musicxml_roundtrip_csv(original_musicxml_dirs,
                                   roundtrip_musicxml_dir,
                                   comparison_output_file):
    """
    Compares original MusicXML files with the round-tripped MusicXML files and
    exports the comparison results to a CSV file.

    Args:
        original_musicxml_dirs: A list of directories containing the original .musicxml files.
        roundtrip_musicxml_dir: The directory containing the round-tripped .musicxml files.
        comparison_output_file: The path to the output CSV file for comparison results.
    """

    original_files = {}
    roundtrip_files = {}
    comparison_results = []

    # Collect original MusicXML files and their base names
    print("original_musicxml_dirs", original_musicxml_dirs)
    for original_dir in original_musicxml_dirs:
        for sample_id_folder in Path(original_dir).iterdir():
            print("sample Id folder", sample_id_folder)
            if not sample_id_folder.is_dir():
                continue

            for xml_file in sample_id_folder.glob("*.musicxml"):
                base_name = f"{sample_id_folder.name}_{xml_file.stem}"
                print("base name", base_name)
                original_files[base_name] = xml_file

    # Collect round-tripped MusicXML files and their expected base names
    roundtrip_path = Path(roundtrip_musicxml_dir)
    if roundtrip_path.is_dir():
        for rt_xml_file in roundtrip_path.glob("*_roundtrip.musicxml"):
            base_name_rt = rt_xml_file.stem.replace("_roundtrip", "")
            roundtrip_files[base_name_rt] = rt_xml_file

    # Compare files based on their base names
    for base_name, original_file in original_files.items():
        result_text = ""
        if base_name in roundtrip_files:
            roundtrip_file = roundtrip_files[base_name]
            are_same = filecmp.cmp(original_file,
                                   roundtrip_file,
                                   shallow=False)
            result_text = "Identical" if are_same else "Different"
        else:
            result_text = "Round-trip file not found"
        comparison_results.append([f"{base_name}.musicxml", result_text])

    print("Comparison Results:")
    with open(comparison_output_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original Filename",
                         "Comparison Result"])  # Write header
        writer.writerows(sorted(comparison_results))
        for row in sorted(comparison_results):
            print(f"  {row[0]}: {row[1]}")


# def compare_musicxml_roundtrip(original_musicxml_dirs, roundtrip_musicxml_dir):
#     """
#     Compares original MusicXML files with the round-tripped MusicXML files.

#     Args:
#         original_musicxml_dirs: A list of directories containing the original .musicxml files.
#         roundtrip_musicxml_dir: The directory containing the round-tripped .musicxml files.
#     """

#     original_files = {}
#     roundtrip_files = {}
#     comparison_results = {}

#     # Collect original MusicXML files and their base names
#     print("original_musicxml_dirs", original_musicxml_dirs)
#     for original_dir in original_musicxml_dirs:
#         for sample_id_folder in Path(original_dir).iterdir():
#             print("sample Id folder", sample_id_folder)
#             if not sample_id_folder.is_dir():
#                 continue

#             for xml_file in sample_id_folder.glob("*.musicxml"):
#                 base_name = f"{sample_id_folder.name}_{xml_file.stem}"
#                 print("base name", base_name)
#                 original_files[base_name] = xml_file

#     # Collect round-tripped MusicXML files and their expected base names
#     roundtrip_path = Path(roundtrip_musicxml_dir)
#     if roundtrip_path.is_dir():
#         for rt_xml_file in roundtrip_path.glob("*_roundtrip.musicxml"):
#             base_name_rt = rt_xml_file.stem.replace("_roundtrip", "")
#             roundtrip_files[base_name_rt] = rt_xml_file

#     # Compare files based on their base names
#     for base_name, original_file in original_files.items():
#         if base_name in roundtrip_files:
#             roundtrip_file = roundtrip_files[base_name]
#             are_same = filecmp.cmp(original_file,
#                                    roundtrip_file,
#                                    shallow=False)
#             comparison_results[base_name] = are_same
#         else:
#             comparison_results[base_name] = "Round-trip file not found"

#     print("Comparison Results:")
#     for base_name, result in comparison_results.items():
#         if result is True:
#             print(f"  {base_name}.musicxml: Identical")
#         elif result is False:
#             print(f"  {base_name}.musicxml: Different")
#         else:
#             print(f"  {base_name}.musicxml: {result}")

if __name__ == "__main__":
    original_dirs = [
        "./olimpic-1.0-synthetic/samples", "./olimpic-1.0-scanned/samples"
    ]
    roundtrip_dir = "./roundtrip_musicxml"
    original_output_file = "original_filenames.txt"
    roundtrip_output_file = "roundtrip_filenames.txt"
    comparison_output_file = "comparison_results.csv"
    # export_filenames(original_dirs, original_output_file)
    # export_roundtrip_filenames(roundtrip_dir, roundtrip_output_file)
    compare_musicxml_roundtrip_csv(original_dirs, roundtrip_dir,
                                   comparison_output_file)

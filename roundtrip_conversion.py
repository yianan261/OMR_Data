import os
import subprocess
from pathlib import Path

hum2xml_path = "/Users/chenyian261/Documents/StevensSpring2025/Olimpic/humdrum_extras_build/humextra/bin/hum2xml"


def kern_to_musicxml(input_kern_file, output_musicxml_file):
    """Converts a Humdrum/Kern file back to MusicXML using hum2xml."""
    try:
        print(f"Processing {input_kern_file} -> {output_musicxml_file}")
        result = subprocess.run(
            [
                hum2xml_path,
                str(input_kern_file), "-o",
                str(output_musicxml_file)
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f" Converted: {input_kern_file} -> {output_musicxml_file.name}")
    except subprocess.CalledProcessError as e:
        print(f" Error converting {input_kern_file}: {e}")
    except FileNotFoundError:
        print(
            " hum2xml command not found. Please ensure it is installed and in your PATH (it's part of Humdrum Extras)."
        )


def round_trip_convert(kern_directory, output_musicxml_directory):
    """Performs round-trip conversion: Kern -> MusicXML."""
    output_musicxml_directory.mkdir(parents=True, exist_ok=True)

    for kern_file in Path(kern_directory).glob("*.krn"):
        output_musicxml_file = output_musicxml_directory / f"{kern_file.stem}_roundtrip.musicxml"
        kern_to_musicxml(kern_file, output_musicxml_file)


if __name__ == "__main__":
    kern_directory = "converted_kern"
    output_musicxml_directory = Path("roundtrip_musicxml")
    round_trip_convert(kern_directory, output_musicxml_directory)

    print(
        f"\nRound-trip conversion finished. MusicXML files are in: {output_musicxml_directory}"
    )
    print(
        "Now you can compare these round-tripped MusicXML files with your original MusicXML files."
    )

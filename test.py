import subprocess

def convert_musicxml_to_kern(input_file, output_file):
    binary_path = "/home/aisec/humlib/bin/musicxml2hum"
    """Converts a MusicXML (.mxl) file to Humdrum/Kern using musicxml2hum binary."""
    try:
        result = subprocess.run(
            [binary_path, str(input_file)],
            capture_output=True,
            text=True,
            check=True
        )
        with open(output_file, "w") as f:
            f.write(result.stdout)
        print(f"✅ Converted: {input_file.name} → {output_file.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed for {input_file.name}: {e}")
        print(e.stderr)
        return False

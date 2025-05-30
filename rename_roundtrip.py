import os
#####################################################################
# util script to normalize file names
#####################################################################

ROUNDTRIP_DIR = "roundtrip_musicxml"

for filename in os.listdir(ROUNDTRIP_DIR):
    if filename.endswith(".musicxml") and "_roundtrip" in filename:
        new_name = filename.replace("_roundtrip", "")
        src = os.path.join(ROUNDTRIP_DIR, filename)
        dst = os.path.join(ROUNDTRIP_DIR, new_name)

        try:
            os.rename(src, dst)
            print(f"Renamed: {filename} → {new_name}")
        except Exception as e:
            print(f"Failed to rename {filename}: {e}")

from datasets import load_dataset, Dataset, DatasetDict
import os

##################################
# old file, no longer needed for ekern
##################################

def combine_grandstaff_with_bekern(bekern_dir):
    """Combines Grandstaff dataset with bekern files."""

    dataset = load_dataset("antoniorv6/grandstaff", split="train")

    bekern_files = []
    bekern_data = []

    # Get the names of the bekern files.
    for filename in os.listdir(bekern_dir):
        if filename.endswith(".bekern"):
            bekern_files.append(filename)

    #Create a dictionary that maps the original dataset image names, to the bekern file names.
    image_to_bekern = {}
    for bekern_file in bekern_files:
        original_image_name = bekern_file.replace(".bekern", ".png")
        image_to_bekern[original_image_name] = bekern_file

    #Check if the original dataset contains the images that the bekern files are based on.
    images_in_dataset = dataset["image_file"]
    for image_name in image_to_bekern.keys():
        if image_name not in images_in_dataset:
            print(
                f"Warning: {image_name} not found in original dataset. Skipping {image_to_bekern[image_name]}"
            )
            del image_to_bekern[image_name]

    #load bekern data.
    for image_name in dataset["image_file"]:
        if image_name in image_to_bekern.keys():
            bekern_file_path = os.path.join(bekern_dir,
                                            image_to_bekern[image_name])
            with open(bekern_file_path, "r") as f:
                bekern_data.append(f.read())
        else:
            bekern_data.append(None)

    # Add bekern data as a new column.
    dataset = dataset.add_column("bekern_transcription", bekern_data)

    # Save the modified dataset.
    dataset.save_to_disk("grandstaff_combined")
    print("Grandstaff dataset combined and saved to grandstaff_combined")


if __name__ == "__main__":
    bekern_dir = "/Users/chenyian261/Documents/StevensSpring2025/Olimpic/bekern_output"
    combine_grandstaff_with_bekern(bekern_dir)

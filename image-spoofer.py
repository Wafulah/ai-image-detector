import argparse
import hashlib
from PIL import Image
import piexif
import os
import multiprocessing


# Function to calculate the hash of an image file
def calculate_file_hash(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
    return hashlib.sha512(file_data).hexdigest()


# Worker function to modify metadata and check for the desired hash prefix
def attempt_modification(args):
    input_path, target_prefix, output_path, attempt = args

    # Load the image
    image = Image.open(input_path)
    exif_dict = piexif.load(image.info.get("exif", piexif.dump({})))

    # Add or modify a custom EXIF tag for hash spoofing
    if "Exif" not in exif_dict:
        exif_dict["Exif"] = {}

    spoofing_key = piexif.ExifIFD.UserComment
    exif_dict["Exif"][spoofing_key] = f"Attempt {attempt}".encode("utf-8")

    # Save the modified image with updated metadata
    modified_exif_bytes = piexif.dump(exif_dict)
    image.save(output_path, exif=modified_exif_bytes)

    # Calculate the hash of the modified file
    modified_hash = calculate_file_hash(output_path)

    # Check if the hash starts with the target prefix
    if modified_hash.startswith(target_prefix):
        return modified_hash
    return None


# Modify image metadata to achieve the desired hash prefix
def modify_metadata_for_target_hash(input_path, target_prefix, output_path, max_attempts=100000, num_workers=4):
    original_hash = calculate_file_hash(input_path)

    # Create tasks for multiprocessing
    tasks = [(input_path, target_prefix, output_path, attempt) for attempt in range(max_attempts)]

    # Use multiprocessing to attempt modifications in parallel
    with multiprocessing.Pool(num_workers) as pool:
        for result in pool.imap_unordered(attempt_modification, tasks):
            if result:  # If a successful modification is found
                return {
                    "original_hash": original_hash,
                    "modified_hash": result,
                    "is_modified": original_hash != result,
                    "output_path": output_path,
                }

    raise ValueError(f"Unable to achieve target hash prefix '{target_prefix}' after {max_attempts} attempts.")


# Main function with argparse for command-line interaction
def main():
    parser = argparse.ArgumentParser(description="Image Hash Spoofing Tool")
    parser.add_argument("target_prefix", type=str, help="Desired hash prefix (hexstring)")
    parser.add_argument("input_image", type=str, help="Path to the input image")
    parser.add_argument("output_image", type=str, help="Path to save the modified image")
    args = parser.parse_args()

    # Perform hash spoofing
    try:
        result = modify_metadata_for_target_hash(args.input_image, args.target_prefix, args.output_image)
        print(f"Original image hash: {result['original_hash']}")
        print(f"Modified image hash: {result['modified_hash']}")
        print(f"Hashes are different: {result['is_modified']}")
        if result['is_modified']:
            print(f"Modified image saved to {result['output_path']}")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()

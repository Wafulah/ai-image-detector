import argparse
import hashlib
from PIL import Image
import numpy as np
import multiprocessing
import os

# Helper function to calculate the SHA-512 hash of an image
def calculate_image_hash(image_path):
    with open(image_path, "rb") as f:
        img_data = f.read()
    return hashlib.sha512(img_data).hexdigest()

# Modify pixels to embed a secret pattern while aiming for a target hash prefix
def modify_image_for_target_hash(image_path, target_hash_prefix, output_path, max_attempts=10000, num_workers=4):
    # Open image and convert to RGB
    image = Image.open(image_path).convert('RGB')
    pixels = np.array(image)
    original_hash = calculate_image_hash(image_path)

    flat_pixels = pixels.flatten()
    modified_pixels = flat_pixels.copy()

    # Initialize a pool for parallel processing
    pool = multiprocessing.Pool(num_workers)

    # Create tasks to modify random pixels
    tasks = []
    for _ in range(max_attempts):
        idx = np.random.randint(len(modified_pixels))
        tasks.append((flat_pixels, pixels.shape, idx, output_path, target_hash_prefix))

    # Process tasks in parallel
    for modified_hash in pool.imap_unordered(attempt_modification, tasks):
        if modified_hash:
            pool.terminate()  # Stop further processing once a match is found
            return {
                "original_hash": original_hash,
                "modified_hash": modified_hash,
                "is_modified": original_hash != modified_hash,
                "output_path": output_path
            }

    raise ValueError(f"Unable to achieve target hash prefix '{target_hash_prefix}' after {max_attempts} attempts.")

# Function to modify a single attempt (used in parallel processing)
def attempt_modification(args):
    flat_pixels, pixels_shape, idx, image_path, target_hash_prefix = args
    modified_pixels = flat_pixels.copy()

    # Modify the pixel
    modified_pixels[idx] = (modified_pixels[idx] + 1) % 256

    # Save the modified image temporarily
    temp_image = Image.fromarray(modified_pixels.reshape(pixels_shape).astype('uint8'))
    temp_image.save(image_path)

    # Check the hash of the modified image
    modified_hash = calculate_image_hash(image_path)
    
    # Return the modified hash if it starts with the target prefix
    if modified_hash.startswith(target_hash_prefix):
        return modified_hash
    return None

# Main function with argparse for command-line interaction
def main():
    parser = argparse.ArgumentParser(description="Image Hash Spoofing Tool")
    parser.add_argument("target_prefix", type=str, help="Desired hash prefix (hexstring)")
    parser.add_argument("input_image", type=str, help="Path to the input image")
    parser.add_argument("output_image", type=str, help="Path to save the modified image")
    args = parser.parse_args()

    # Perform hash spoofing
    try:
        result = modify_image_for_target_hash(args.input_image, args.target_prefix, args.output_image)
        print(f"Original image hash: {result['original_hash']}")
        print(f"Modified image hash: {result['modified_hash']}")
        print(f"Hashes are different: {result['is_modified']}")
        if result['is_modified']:
            print(f"Modified image saved to {result['output_path']}")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()

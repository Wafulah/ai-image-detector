import argparse
import hashlib
import math
import os
import random
import piexif
from PIL import Image
import multiprocessing


# Function to calculate the hash of a file
def calculate_file_hash(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
    return hashlib.sha512(file_data).hexdigest()


# Simulated Annealing Attempt
def simulated_annealing_attempt(input_path, target_prefix, output_path, max_attempts, initial_temp, cooling_rate, seed):
    
    #Perform hash spoofing using Simulated Annealing to modify image metadata.
    
    random.seed(seed)  # Set seed for reproducibility
    original_hash = calculate_file_hash(input_path)

    # Load the image and metadata
    image = Image.open(input_path)
    exif_dict = piexif.load(image.info.get("exif", piexif.dump({})))

    if "Exif" not in exif_dict:
        exif_dict["Exif"] = {}

    spoofing_key = piexif.ExifIFD.UserComment
    exif_dict["Exif"].setdefault(spoofing_key, b"Initial Spoof")

    # Initialize Simulated Annealing parameters
    current_temp = initial_temp
    best_hash = original_hash
    best_metadata = exif_dict.copy()

    for attempt in range(max_attempts):
        # Generate a new random modification
        random_change = random.randint(0, 1000)
        exif_dict["Exif"][spoofing_key] = f"Attempt {random_change}".encode("utf-8")

        # Save the modified image
        modified_exif_bytes = piexif.dump(exif_dict)
        image.save(output_path, exif=modified_exif_bytes)

        # Calculate the new hash
        modified_hash = calculate_file_hash(output_path)

        # Check if we found the target prefix
        if modified_hash.startswith(target_prefix):
            return modified_hash

        # Calculate hash similarity (distance from the target prefix)
        current_similarity = hash_similarity(modified_hash, target_prefix)
        best_similarity = hash_similarity(best_hash, target_prefix)

        # Simulated Annealing logic
        if current_similarity > best_similarity or random.random() < acceptance_probability(current_temp, current_similarity, best_similarity):
            best_hash = modified_hash
            best_metadata = exif_dict.copy()

        # Cool down the temperature
        current_temp *= cooling_rate

    # Restore the best found solution
    modified_exif_bytes = piexif.dump(best_metadata)
    image.save(output_path, exif=modified_exif_bytes)

    return None  # No successful match found


# Helper Functions for Simulated Annealing
def hash_similarity(current_hash, target_prefix):
    """
    Compute similarity as the number of matching characters from the start.
    """
    match_length = 0
    for c1, c2 in zip(current_hash, target_prefix):
        if c1 == c2:
            match_length += 1
        else:
            break
    return match_length


def acceptance_probability(temperature, new_similarity, old_similarity):
    """
    Calculate the probability of accepting a worse solution.
    """
    if new_similarity > old_similarity:
        return 1.0
    return math.exp((new_similarity - old_similarity) / temperature)


# Multiprocessing Integration
def modify_metadata_with_multiprocessing(input_path, target_prefix, output_path, max_attempts=100000, num_workers=4, initial_temp=1000, cooling_rate=0.99):
    original_hash = calculate_file_hash(input_path)

    # Create tasks for multiprocessing
    tasks = [
        (input_path, target_prefix, output_path, max_attempts // num_workers, initial_temp, cooling_rate, seed)
        for seed in range(num_workers)
    ]

    # Use multiprocessing to parallelize Simulated Annealing attempts
    with multiprocessing.Pool(num_workers) as pool:
        for result in pool.imap_unordered(simulated_annealing_attempt_wrapper, tasks):
            if result:  # If a successful modification is found
                return {
                    "original_hash": original_hash,
                    "modified_hash": result,
                    "is_modified": original_hash != result,
                    "output_path": output_path,
                }

    raise ValueError(f"Unable to achieve target hash prefix '{target_prefix}' after {max_attempts} attempts.")


def simulated_annealing_attempt_wrapper(args):
    return simulated_annealing_attempt(*args)


# Main function with argparse for command-line interaction
def main():
    parser = argparse.ArgumentParser(description="Image Hash Spoofing Tool with Simulated Annealing and Multiprocessing")
    parser.add_argument("target_prefix", type=str, help="Desired hash prefix (hexstring, without 0x)")
    parser.add_argument("input_image", type=str, help="Path to the input image")
    parser.add_argument("output_image", type=str, help="Path to save the modified image")
    parser.add_argument("--max_attempts", type=int, default=100000, help="Maximum number of attempts (default: 100000)")
    parser.add_argument("--num_workers", type=int, default=4, help="Number of parallel workers (default: 4)")
    parser.add_argument("--initial_temp", type=float, default=1000, help="Initial temperature for Simulated Annealing (default: 1000)")
    parser.add_argument("--cooling_rate", type=float, default=0.99, help="Cooling rate for Simulated Annealing (default: 0.99)")
    args = parser.parse_args()

    # Validate target_prefix
    if not all(c in "0123456789abcdef" for c in args.target_prefix.lower()):
        print("Error: target_prefix must be a valid hex string.")
        return

    # Perform hash spoofing
    try:
        result = modify_metadata_with_multiprocessing(
            args.input_image,
            args.target_prefix,
            args.output_image,
            max_attempts=args.max_attempts,
            num_workers=args.num_workers,
            initial_temp=args.initial_temp,
            cooling_rate=args.cooling_rate,
        )
        print(f"Original image hash: {result['original_hash']}")
        print(f"Modified image hash: {result['modified_hash']}")
        print(f"Hashes are different: {result['is_modified']}")
        if result['is_modified']:
            print(f"Modified image saved to {result['output_path']}")
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()

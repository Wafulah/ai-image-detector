import argparse
import hashlib
import math
import os
import io
import random
import piexif
from PIL import Image
import multiprocessing
import cProfile
import pstats

# Function to calculate the hash of a file
def calculate_file_hash(file_path, algorithm="sha512"):
    """
    Calculate the hash of a file using a specified algorithm.

    Parameters:
        file_path (str): Path to the file.
        algorithm (str): Hash algorithm to use (e.g., "sha256", "sha512", "sha1").

    Returns:
        str: Hexadecimal hash of the file.
    """
    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, "rb") as f:
        file_data = f.read()
    hash_func.update(file_data)
    return hash_func.hexdigest()


# Simulated Annealing Attempt
def simulated_annealing_attempt(input_path, target_prefix, output_path, max_attempts, initial_temp, cooling_rate, seed, algorithm):
    """
    Perform hash spoofing using Simulated Annealing to modify image metadata.

    Parameters:
        input_path (str): Path to the input image.
        target_prefix (str): Desired hash prefix.
        output_path (str): Path to save the modified image.
        max_attempts (int): Maximum number of attempts.
        initial_temp (float): Initial temperature for annealing.
        cooling_rate (float): Cooling rate for temperature decay.
        seed (int): Seed for random number generation.
        algorithm (str): Hash algorithm to use.

    Returns:
        str or None: Modified hash if successful; otherwise, None.
    """
    random.seed(seed)
    original_hash = calculate_file_hash(input_path, algorithm)

    try:
        image = Image.open(input_path)
        exif_dict = piexif.load(image.info.get("exif", piexif.dump({})))
    except Exception as e:
        print(f"Error loading image or EXIF data: {e}")
        return None

    if "Exif" not in exif_dict:
        exif_dict["Exif"] = {}

    spoofing_key = piexif.ExifIFD.UserComment
    exif_dict["Exif"].setdefault(spoofing_key, b"Initial Spoof")

    current_temp = initial_temp
    best_hash = original_hash
    best_metadata = exif_dict.copy()

    for attempt in range(max_attempts):
        random_change = random.randint(0, 1000)
        exif_dict["Exif"][spoofing_key] = f"Attempt {random_change}".encode("utf-8")

        try:
            modified_exif_bytes = piexif.dump(exif_dict)
            image.save(output_path, exif=modified_exif_bytes)
        except Exception as e:
            print(f"Error saving image with modified metadata: {e}")
            continue

        modified_hash = calculate_file_hash(output_path, algorithm)

        if modified_hash.startswith(target_prefix):
            return modified_hash

        current_similarity = hash_similarity(modified_hash, target_prefix)
        best_similarity = hash_similarity(best_hash, target_prefix)

        if current_similarity > best_similarity or random.random() < acceptance_probability(current_temp, current_similarity, best_similarity):
            best_hash = modified_hash
            best_metadata = exif_dict.copy()

        current_temp *= cooling_rate

    try:
        modified_exif_bytes = piexif.dump(best_metadata)
        image.save(output_path, exif=modified_exif_bytes)
    except Exception as e:
        print(f"Error restoring best metadata: {e}")

    return None


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
    return math.exp((new_similarity - old_similarity) / max(temperature, 1e-10))


# Multiprocessing Integration
def modify_metadata_with_multiprocessing(input_path, target_prefix, output_path, max_attempts=100000, num_workers=4, initial_temp=1000, cooling_rate=0.99, algorithm="sha512"):
    original_hash = calculate_file_hash(input_path, algorithm)

    tasks = [
        (input_path, target_prefix, output_path, max_attempts // num_workers, initial_temp, cooling_rate, seed, algorithm)
        for seed in range(num_workers)
    ]

    with multiprocessing.Pool(num_workers) as pool:
        for result in pool.imap_unordered(simulated_annealing_attempt_wrapper, tasks):
            if result:
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
    parser.add_argument("--hash_algorithm", type=str, default="sha512", choices=["sha256", "sha512", "sha1"],
                        help="Hash algorithm to use (default: sha512)")
    args = parser.parse_args()

    if not all(c in "0123456789abcdef" for c in args.target_prefix.lower()):
        print("Error: target_prefix must be a valid hex string.")
        return

    try:
        result = modify_metadata_with_multiprocessing(
            args.input_image,
            args.target_prefix,
            args.output_image,
            max_attempts=args.max_attempts,
            num_workers=args.num_workers,
            initial_temp=args.initial_temp,
            cooling_rate=args.cooling_rate,
            algorithm=args.hash_algorithm,
        )
        print(f"Original image hash: {result['original_hash']}")
        print(f"Modified image hash: {result['modified_hash']}")
        print(f"Hashes are different: {result['is_modified']}")
        if result['is_modified']:
            print(f"Modified image saved to {result['output_path']}")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Profile the code
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Call the main function or script logic
    main()
    
    # Disable profiler and generate a report
    profiler.disable()
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    
    # Sort by cumulative time and display top 20 results
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)
    
    # Print the structured report
    print(stream.getvalue())

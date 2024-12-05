import hashlib
from PIL import Image
import numpy as np
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

# Secret pattern to embed in the image's hash
SECRET_PATTERN = "DEADBEEF"  # Modify as needed
PATTERN_HEX = bytes.fromhex(SECRET_PATTERN)

# Helper function to calculate the SHA-512 hash of an image
def calculate_image_hash(image_path, hash_algo='sha512'):
    with open(image_path, "rb") as f:
        img_data = f.read()
    if hash_algo == 'sha512':
        return hashlib.sha512(img_data).hexdigest()
    else:
        raise ValueError("Unsupported hash algorithm")

# Gradient-based method to strategically modify pixel values
def modify_pixel_gradient(pixels, pattern_bits, start_index, end_index):
    flat_pixels = pixels.flatten()
    byte_index = start_index
    modified_pixels = flat_pixels.copy()

    for i in range(start_index, end_index, 3):  # Go through each pixel (RGB)
        if byte_index < len(pattern_bits):
            # Modify the least significant bit (LSB) of the red channel
            red_channel = modified_pixels[i]  # Red channel value
            # Alter the least significant bit of the red channel
            red_channel = (red_channel & 0xFE) | int(pattern_bits[byte_index])
            modified_pixels[i] = red_channel  # Set the modified red channel
            byte_index += 1

        if byte_index == len(pattern_bits):  # If the whole pattern is embedded
            break

    return modified_pixels, byte_index

# Function to modify the image to embed the secret pattern
def modify_image_for_secret_signature(image_path, target_hash_prefix, output_path):
    # Open image and convert to a numpy array for pixel manipulation
    image = Image.open(image_path)
    image = image.convert('RGB')
    pixels = np.array(image)
    original_hash = calculate_image_hash(image_path)


    # Create the binary representation of the secret pattern (secret pattern in bytes)
    pattern_bits = ''.join(f"{byte:08b}" for byte in PATTERN_HEX)

    # Use multiprocessing to modify the image in parallel
    num_processes = 4  # Number of processes to use
    chunk_size = len(pattern_bits) // num_processes

    # Prepare the indices for dividing the work
    ranges = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], len(pattern_bits))  # Ensure the last process covers any remainder

    # Create a pool of workers to modify the pixels in parallel
    modified_pixels = pixels.flatten()
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = []
        for start_index, end_index in ranges:
            futures.append(executor.submit(modify_pixel_gradient, pixels, pattern_bits, start_index, end_index))

        # Collect results
        byte_index = 0
        for future in futures:
            modified_pixels_chunk, byte_index = future.result()
            modified_pixels = modified_pixels_chunk

    # Reshape the array back to the original shape
    modified_pixels = modified_pixels.reshape(pixels.shape)
    modified_image = Image.fromarray(modified_pixels.astype('uint8'))
    
    # Save the modified image temporarily to check its hash
    modified_image.save(output_path)

    # Check if the hash of the modified image starts with the target prefix
    image_hash = calculate_image_hash(output_path)
    modified = image_hash.startswith(target_hash_prefix)

    return {
    "original_hash": original_hash,
    "modified_hash": image_hash,
    "is_modified": original_hash != image_hash,
    "modified_image": modified_image
}

# Main execution function
def main():
    # Input and output paths for the image
    input_image = "original_image.jpg"  # Path to the original image
    output_image = "modified_image.jpg"  # Path to save the modified image
    target_hash_prefix = "2448a6512f"  # Hex string to be the prefix of the image hash (change as needed)

    # Modify the image and get the hashes
    result = modify_image_for_secret_signature(input_image, target_hash_prefix, output_image)

    # Display results
    print(f"Original image hash: {result['original_hash']}")
    print(f"Modified image hash: {result['modified_hash']}")
    print(f"Hashes are different: {result['is_modified']}")
    if result['is_modified']:
        print(f"Modified image saved to {output_image}")

# Run the program
if __name__ == "__main__":
    main()

# Image Hash Spoofing Tool

## Overview
This tool provides a robust mechanism to modify image metadata using **Simulated Annealing** with multiprocessing to achieve a target hash prefix. It is ideal for applications where file integrity verification is critical, such as:

- Watermarking
- Digital rights management
- Forensic research

By integrating cryptographic techniques, advanced optimization methods, and parallel processing, this script showcases state-of-the-art problem-solving in Python.

## Features

### Simulated Annealing Optimization
- Implements a probabilistic method to explore metadata modifications, balancing exploration and exploitation.
- Incorporates cooling mechanisms to converge on optimal solutions.

### Multiprocessing
- Uses multiple workers to parallelize attempts, significantly improving performance for large search spaces.

### Robust CLI
- Configurable parameters for hash prefix, temperature, cooling rate, and the number of workers.

### Metadata Manipulation
- Uses the `piexif` library to inject modifications into EXIF metadata without altering image quality.

## Requirements
The script requires the following dependencies:

- **Python** 3.7+
- **Pillow**: `pip install pillow`
- **piexif**: `pip install piexif`

## How It Works

### Process Flow

1. **Input**: Provide an image file and a target hash prefix to achieve.
2. **Hash Calculation**: Uses `SHA-512` to calculate the image's hash.
3. **Simulated Annealing**:
   - Randomly modifies the EXIF metadata.
   - Evaluates the hash against the target prefix.
   - Uses probabilistic acceptance for non-optimal solutions based on temperature.
4. **Multiprocessing**: Distributes the simulated annealing process across multiple workers.
5. **Output**: Saves the modified image once the target hash prefix is achieved.

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/image-hash-spoofing.git
cd image-hash-spoofing
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script from the command line with the following syntax:

```bash
python hash_spoof.py <target_prefix> <input_image> <output_image> [--max_attempts N] [--num_workers W] [--initial_temp T] [--cooling_rate R]
```

### Arguments

| Argument       | Type    | Description                                                  |
|----------------|---------|--------------------------------------------------------------|
| `target_prefix`| String  | Desired hash prefix (hexadecimal).                           |
| `input_image`  | String  | Path to the input image.                                     |
| `output_image` | String  | Path to save the modified image.                            |
| `--max_attempts`| Integer | Maximum number of modification attempts (default: 100,000). |
| `--num_workers`| Integer | Number of parallel workers for multiprocessing (default: 4). |
| `--initial_temp`| Float   | Initial temperature for simulated annealing (default: 1000).|
| `--cooling_rate`| Float   | Cooling rate for temperature decay (default: 0.99).         |

### Example

```bash
python hash_spoof.py f8b2 "input.jpg" "output.jpg" --max_attempts 50000 --num_workers 6 --initial_temp 1200 --cooling_rate 0.98
```

## Code Breakdown

### Key Components

#### `calculate_file_hash(file_path)`
- Reads a file in binary mode and computes its SHA-512 hash.

#### `simulated_annealing_attempt()`
- Core function that performs Simulated Annealing to modify the EXIF metadata iteratively.

#### Helper Functions

- `hash_similarity(current_hash, target_prefix)`: Measures how close a hash is to the desired prefix.
- `acceptance_probability(temperature, new_similarity, old_similarity)`: Determines the probability of accepting a worse solution to escape local optima.

#### `modify_metadata_with_multiprocessing()`
- Leverages the `multiprocessing` module to run multiple Simulated Annealing attempts in parallel.

#### CLI
- The `argparse` module enables command-line interaction for user customization.

## Results

### Output Image
- The modified image is saved to the specified path.

### Hashes
- The script prints the original and modified hash, along with success status.

## Performance
The tool uses advanced techniques to ensure efficiency:

- **Simulated Annealing** minimizes unnecessary iterations.
- **Multiprocessing** distributes computational tasks, reducing runtime on multi-core processors.

## Limitations

- **Computationally Intensive**: High `--max_attempts` and many workers can strain resources.
- **Dependency on Metadata**: Some images may lack editable EXIF metadata.

## Applications

- **Security Research**: Testing hash collision vulnerabilities.
- **Digital Forensics**: Manipulating and analyzing file integrity.
- **Data Watermarking**: Customizing image metadata for branding.

## Future Improvements

- **Enhanced Hash Functions**: Support other hashing algorithms (e.g., MD5, SHA-256).
- **GUI Interface**: Add a user-friendly interface for broader usability.
- **Dynamic Metadata**: Automatically identify other editable metadata fields.

## Author
**Victor Wafula Simiyu**  
Software Engineer | Optimization Specialist

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

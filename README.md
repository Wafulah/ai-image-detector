# Image Hash Spoofing Tool: Simulated Annealing with Multiprocessing

## Overview

This tool is a Python-based implementation that modifies an image's metadata to achieve a desired **SHA-512 hash prefix**. It combines **Simulated Annealing** and **Multiprocessing** for efficient, parallelized exploration of the solution space. By using this tool, you can experiment with cryptographic concepts like hash collisions and explore metadata manipulation in images.

---

## How It Works

### General Workflow

1. **Input**:
   - The user provides:
     - `An input image file`: The image whose metadata will be modified.
     - `A target hash prefix`: The desired starting characters of the hash.
   - Optional parameters include:
     - Maximum attempts.
     - Number of workers.
     - Initial temperature for simulated annealing.
     - Cooling rate for temperature decay.

2. **Hash Calculation**:
   - The image's hash is computed using the **SHA-512 algorithm**.

3. **Simulated Annealing**:
   - The EXIF metadata of the image is **randomly modified**.
   - Each modification is evaluated against the target prefix.
   - A probabilistic acceptance criterion ensures that non-optimal changes are sometimes accepted, allowing the algorithm to escape local minima.

4. **Multiprocessing**:
   - The simulated annealing process is distributed across multiple workers, each running independently with a unique random seed.

5. **Output**:
   - Once the desired hash prefix is achieved, the tool saves the modified image to the specified location.

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/Wafulah/ai-image-detector.git
cd image-hash-spoofing
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

Run the script from the command line using the following syntax:

```bash
python image-spoofer.py <target_prefix> <input_image> <output_image> [--max_attempts N] [--num_workers W] [--initial_temp T] [--cooling_rate R]
```

### Arguments

| Argument         | Type    | Description                                                 |
|------------------|---------|-------------------------------------------------------------|
| `target_prefix`  | String  | Desired hash prefix (hexadecimal).                          |
| `input_image`    | String  | Path to the input image.                                    |
| `output_image`   | String  | Path to save the modified image.                           |
| `--max_attempts` | Integer | Maximum number of modification attempts (default: 100,000).|
| `--num_workers`  | Integer | Number of parallel workers for multiprocessing (default: 4).|
| `--initial_temp` | Float   | Initial temperature for simulated annealing (default: 1000).|
| `--cooling_rate` | Float   | Cooling rate for temperature decay (default: 0.99).        |

### Example

```bash
python image-spoofer.py f8b2 "input.jpg" "output.jpg" --max_attempts 50000 --num_workers 6 --initial_temp 1200 --cooling_rate 0.98
```

---

## Code Breakdown

### Key Components

1. **`calculate_file_hash(file_path)`**
   - Reads the binary content of the image file.
   - Computes the SHA-512 hash.
   - Used to evaluate if the hash matches the desired prefix.

2. **`simulated_annealing_attempt()`**
   - Performs Simulated Annealing:
     - Randomly modifies the `UserComment` EXIF field of the image metadata.
     - Evaluates the modified hash's similarity to the target prefix.
     - Uses probabilistic logic to accept changes based on temperature and similarity.

3. **`hash_similarity(current_hash, target_prefix)`**
   - Measures the number of matching characters between the hash and the target prefix.
   - Guides the algorithm toward better solutions.

4. **`acceptance_probability(temperature, new_similarity, old_similarity)`**
   - Implements the Simulated Annealing acceptance rule:
     - Accepts better solutions outright.
     - Accepts worse solutions probabilistically, depending on the temperature.

5. **`modify_metadata_with_multiprocessing()`**
   - Divides the computational workload among multiple workers.
   - Each worker executes `simulated_annealing_attempt()` independently, using unique random seeds.

---

## Simulated Annealing Explained

### What is Simulated Annealing?
Simulated Annealing is an optimization technique inspired by the physical annealing process, where a material is heated and then slowly cooled to achieve a stable state.

### How It Works in This Code:

1. **Initialization**:
   - Start with the original hash and metadata.
   - Set an initial temperature.

2. **Random Modification**:
   - Change the `UserComment` field with a random value.

3. **Evaluation**:
   - Compare the modified hash to the target prefix using `hash_similarity()`.

4. **Acceptance Logic**:
   - If the modification improves the hash, accept it.
   - If the modification worsens the hash, accept it with a probability determined by the current temperature.

5. **Cooling**:
   - Gradually reduce the temperature, focusing the search on fine-tuned improvements.

6. **Termination**:
   - Stop when the target prefix is achieved or the maximum attempts are reached.

---

## Multiprocessing Explained

### Why Use Multiprocessing?
Simulated Annealing can be computationally intensive. By running multiple independent annealing processes in parallel, the solution space is explored more efficiently.

### How It's Implemented:

1. **Task Division**:
   - The total number of attempts is split evenly across multiple workers.

2. **Independent Execution**:
   - Each worker runs `simulated_annealing_attempt()` with a unique random seed.

3. **Result Aggregation**:
   - Workers report back as soon as one of them achieves the desired hash prefix.

---

## How We Achieve Exceptional Performance

### Factors Contributing to Speed:

1. **Simulated Annealing**:
   - Focuses on promising areas of the solution space, avoiding exhaustive brute force.

2. **Multiprocessing**:
   - Utilizes multiple CPU cores to explore independent solution paths simultaneously.

3. **Efficient Hash Evaluation**:
   - Calculates and compares hashes incrementally, minimizing unnecessary computation.

### Pseudocode Representation

```plaintext
1. Read the input image and calculate its hash.
2. Initialize Simulated Annealing parameters (temperature, cooling rate, etc.).
3. Divide tasks among multiple workers:
   - Each worker performs:
     a. Randomly modify image metadata.
     b. Calculate the hash of the modified image.
     c. Compare the hash with the target prefix.
     d. Accept or reject the change based on Simulated Annealing rules.
     e. Repeat until a match is found or attempts are exhausted.
4. Combine results from all workers.
5. Save the modified image if the target prefix is achieved.
```

---

## Output

### If Successful:
- Saves the modified image to the specified `output_image` path.
- Prints the original and modified hashes.

### If Unsuccessful:
- Reports failure after exhausting all attempts.

---

## Potential Applications

- **Research**:
  - Explore hash collision vulnerabilities.
- **Security**:
  - Test hash-based integrity checks.
- **Digital Forensics**:
  - Embed metadata for tracking or identification.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

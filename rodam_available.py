import hashlib
import json
import os

def calculate_sha256(file_path):
    """Calculates the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks to avoid using too much memory
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None

def main():
    # Files to process
    files_to_hash = ["FormatTable.gz", "TR000.zip", "TR002.zip"]
    output_filename = "rodam_available.json"
    
    results = {}
    
    print("Calculating checksums...")
    
    for filename in files_to_hash:
        # Assuming files are in the same directory as the script
        # If not, os.path.join should be used with the correct path
        file_path = os.path.join(os.getcwd(), filename)
        
        checksum = calculate_sha256(file_path)
        
        if checksum:
            print(f"{filename}: {checksum}")
            results[filename] = checksum
        else:
            print(f"Failed to calculate checksum for {filename} (File not found or error)")

    # Save to JSON
    try:
        with open(output_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)
        print(f"\nSuccessfully saved checksums to {output_filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")

if __name__ == "__main__":
    main()

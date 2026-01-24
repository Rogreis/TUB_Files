import hashlib
import json
import os
from dataclasses import dataclass, asdict
from typing import List

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

@dataclass
class RodamManifestItem:
    FileName: str = ""
    FilePath: str = ""
    Optional: bool = False
    Hash256: str = ""

    @staticmethod
    def save_to_manifest(items: List['RodamManifestItem']):
        """Serializes a list of RodamManifestItem objects to rodam_manifest.json."""
        output_filename = "rodam_manifest.json"
        try:
            with open(output_filename, "w", encoding='utf-8') as json_file:
                json.dump([asdict(item) for item in items], json_file, indent=4)
            print(f"Successfully saved manifest to {output_filename}")
        except Exception as e:
            print(f"Error saving manifest to {output_filename}: {e}")

def main():
    # Files to process
    items = [
        RodamManifestItem(FileName="FormatTable.gz", FilePath=""),
        RodamManifestItem(FileName="TR000.zip", FilePath=""),
        RodamManifestItem(FileName="TR002.zip", FilePath=""),
        RodamManifestItem(FileName="tub_modelo_meta.pkl", FilePath=os.path.join("semantic", "model",), Optional=True),
        RodamManifestItem(FileName="tub_modelo.index", FilePath=os.path.join("semantic", "model"), Optional=True)
    ]
    
    print("Calculating checksums and generating manifest...")
    
    for item in items:
        # Construct full path
        full_path = os.path.join(os.getcwd(), item.FilePath, item.FileName)
        
        checksum = calculate_sha256(full_path)
        
        if checksum:
            print(f"{item.FileName}: {checksum}")
            item.Hash256 = checksum
        else:
            print(f"Failed to calculate checksum for {item.FileName} (File not found or error at {full_path})")

    # Save to Manifest
    RodamManifestItem.save_to_manifest(items)

if __name__ == "__main__":
    main()

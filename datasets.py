"""
Downloads a REDUCED subset of cough audio datasets from Kaggle using kagglehub.
Only downloads a small sample from each dataset to conserve disk space.
"""
import kagglehub
import os
import shutil
import random
from pathlib import Path

# --- Configuration ---
# List of datasets to download
DATASETS = [
    "vbookshelf/respiratory-sound-database",
    "andrewmvd/covid19-cough-audio-classification",
    "ruchikashirsath/tb-audio"
]

# Directory to save the downloaded datasets
DOWNLOAD_DIR = Path("./kaggle_datasets")

# Maximum number of audio files to keep from each dataset
MAX_FILES_PER_DATASET = {
    "vbookshelf/respiratory-sound-database": 10,      # ~10 MB (was 3.7 GB)
    "andrewmvd/covid19-cough-audio-classification": 10,  # ~10 MB (was 1 GB)
    "ruchikashirsath/tb-audio": 10                      # ~10 MB (was 2 GB)
}

# --- Helper Functions ---
def reduce_dataset_size(dataset_path, dataset_slug, max_files):
    """
    Keeps only a random sample of audio files from the dataset to reduce size.
    Deletes all other files.
    """
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    # Find all audio files
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(dataset_path.rglob(f"*{ext}"))
    
    print(f"  Found {len(audio_files)} audio files")
    
    if len(audio_files) <= max_files:
        print(f"  Keeping all {len(audio_files)} files (under limit of {max_files})")
        return
    
    # Randomly select files to keep
    files_to_keep = set(random.sample(audio_files, max_files))
    
    # Delete all other files
    deleted_count = 0
    for audio_file in audio_files:
        if audio_file not in files_to_keep:
            try:
                audio_file.unlink()
                deleted_count += 1
            except:
                pass
    
    print(f"  Deleted {deleted_count} files, keeping {max_files} sample files (~{max_files * 1}MB)")

# --- Main Download Logic ---
def download_all_datasets():
    """
    Downloads datasets from Kaggle and reduces their size to only keep a sample.
    This conserves disk space while maintaining dataset diversity.
    """
    print("Starting REDUCED dataset download process...")
    print(f"Datasets will be saved to: {DOWNLOAD_DIR.resolve()}")
    print(f"Max files per dataset: {list(MAX_FILES_PER_DATASET.values())}")
    
    if not DOWNLOAD_DIR.exists():
        DOWNLOAD_DIR.mkdir(parents=True)
        print(f"Created directory: {DOWNLOAD_DIR}")

    for dataset_slug in DATASETS:
        print("\n" + "="*50)
        print(f"Downloading: {dataset_slug}")
        
        try:
            # Download the full dataset. The path to the downloaded files is returned.
            dataset_path = kagglehub.dataset_download(dataset_slug)
            print(f"✓ Successfully downloaded '{dataset_slug}'")
            print(f"  Location: {dataset_path}")
            
            # Reduce dataset size by keeping only a sample
            max_files = MAX_FILES_PER_DATASET.get(dataset_slug, 50)
            print(f"  Reducing to {max_files} sample files...")
            reduce_dataset_size(Path(dataset_path), dataset_slug, max_files)
            
            # List remaining contents to verify
            print("  Sample contents after reduction:")
            try:
                for item in os.listdir(dataset_path)[:3]:  # Show first 3 items
                    print(f"  - {item}")
            except:
                pass

        except Exception as e:
            print(f"✗ ERROR downloading '{dataset_slug}': {e}")
            print("  Please ensure you have authenticated with Kaggle.")
            print("  Instructions: https://www.kaggle.com/docs/api")

    print("\n" + "="*50)
    print("All dataset downloads attempted.")
    print("Check the output above for the status of each download.")

if __name__ == "__main__":
    # Ensure you have run 'kaggle login' or have your kaggle.json configured
    download_all_datasets()



"""
Extract COVID-19 audio files from the andrewmvd/covid19-cough-audio-classification dataset
and organize them into the audio_data folder.
"""

import os
import shutil
import csv
from pathlib import Path
from collections import defaultdict

# Path to the kagglehub cache
CACHE_BASE = Path.home() / '.cache' / 'kagglehub' / 'datasets'
COVID19_DATASET_PATH = CACHE_BASE / 'andrewmvd' / 'covid19-cough-audio-classification' / 'versions' / '1'
METADATA_CSV = COVID19_DATASET_PATH / 'metadata_compiled.csv'
OUTPUT_DIR = Path('./audio_data')

AUDIO_EXTENSIONS = {'.wav'}

def load_metadata():
    """Load metadata from the CSV file."""
    metadata = {}
    
    if not METADATA_CSV.exists():
        print(f"❌ Metadata file not found at {METADATA_CSV}")
        return metadata
    
    try:
        with open(METADATA_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                uuid = row.get('uuid', '').strip()
                status = row.get('status', '').strip().lower()
                if uuid and status in ['healthy', 'covid-19']:
                    metadata[uuid] = status.replace('-', '-').capitalize() if status == 'covid-19' else 'Healthy'
    except Exception as e:
        print(f"❌ Error reading metadata: {e}")
    
    return metadata

def extract_covid19_files():
    """Extract COVID-19 and Healthy files from the dataset."""
    
    if not COVID19_DATASET_PATH.exists():
        print(f"❌ Dataset not found at {COVID19_DATASET_PATH}")
        return
    
    print(f"Loading metadata...")
    metadata = load_metadata()
    print(f"  ✓ Found {len(metadata)} classified files in metadata")
    print()
    
    print(f"Searching for COVID-19 audio files...")
    print(f"Source: {COVID19_DATASET_PATH}")
    print()
    
    organized = defaultdict(list)
    
    # Find all audio files
    for audio_file in COVID19_DATASET_PATH.iterdir():
        if not audio_file.is_file():
            continue
        
        # Check if it's an audio file
        if audio_file.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        
        # Extract UUID from filename
        uuid = audio_file.stem  # Remove extension
        
        # Look up classification
        disease = metadata.get(uuid)
        
        if disease:
            # Copy file to organized directory
            disease_dir = OUTPUT_DIR / disease
            disease_dir.mkdir(parents=True, exist_ok=True)
            
            dest_file = disease_dir / audio_file.name
            
            try:
                # Only copy if not already present
                if not dest_file.exists():
                    shutil.copy2(audio_file, dest_file)
                    organized[disease].append(str(audio_file.name))
                    print(f"  ✓ Copied: {audio_file.name} → {disease}/")
            except Exception as e:
                print(f"  ✗ Error copying {audio_file.name}: {e}")
    
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    
    total_copied = sum(len(files) for files in organized.values())
    print(f"\n✓ Successfully extracted and organized {total_copied} files")
    
    for disease in sorted(organized.keys()):
        files = organized[disease]
        print(f"  {disease}: {len(files)} files")
    
    # Show final count by disease
    print("\n" + "="*60)
    print("FINAL DISTRIBUTION IN audio_data/")
    print("="*60)
    
    for disease_dir in sorted(OUTPUT_DIR.glob('*')):
        if disease_dir.is_dir():
            file_count = len(list(disease_dir.glob('*.wav')))
            print(f"  {disease_dir.name:20s}: {file_count:4d} files")
    
    print()

if __name__ == "__main__":
    extract_covid19_files()

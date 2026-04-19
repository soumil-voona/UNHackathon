"""
Kaggle Dataset Downloader and Organizer for Respiratory Sound Database.
Downloads and organizes the Respiratory Sound Database from Kaggle.

Prerequisites:
    1. Install Kaggle CLI: pip install kaggle
    2. Download API key from Kaggle:
       - Go to https://www.kaggle.com/settings/account
       - Click "Create New API Token"
       - Place kaggle.json in ~/.kaggle/

Usage:
    python download_dataset.py [--dataset-name NAME] [--output OUTPUT]
    
Examples:
    # Download default dataset
    python download_dataset.py
    
    # Download specific dataset
    python download_dataset.py --dataset-name "vbookshelf/respiratory-sound-database"
    
    # Download to custom location
    python download_dataset.py --output ./my_data
"""

import os
import sys
import argparse
from pathlib import Path
import json
import shutil
import subprocess


# Supported datasets on Kaggle
KAGGLE_DATASETS = {
    'respiratory': {
        'name': 'vbookshelf/respiratory-sound-database',
        'description': 'Respiratory Sound Database - Crackles, Wheezes, Normal, Undetermined',
        'size': '~2.5 GB',
        'samples': '920+ recordings',
    },
    'coughvid': {
        'name': 'vbookshelf/coughvid-a-large-scale-open-source-cough-audio-dataset',
        'description': 'COUGHVID - Large scale cough audio dataset',
        'size': '~7 GB',
        'samples': '25,000+',
    },
    'urban-sound': {
        'name': 'pavansanagapati/urban-sound-classification',
        'description': 'Urban Sound Classification',
        'size': '~6 GB',
        'samples': '8,732',
    },
}

# Mapping of sound labels to our disease classes
SOUND_MAPPING = {
    'normal': 'Healthy',
    'crackles': 'Bronchitis',  # Often associated with bronchitis
    'wheezes': 'Asthma',  # Often associated with asthma
    'both': 'Bronchitis',  # Both crackles and wheezes
    'undetermined': 'Healthy',  # Undetermined - categorize as healthy if unsure
}


def check_kaggle_setup():
    """Check if Kaggle CLI is properly configured."""
    print("Checking Kaggle setup...")
    
    try:
        result = subprocess.run(
            ['kaggle', '--version'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Kaggle CLI not found. Install with: pip install kaggle")
            return False
        
        print(f"✓ Kaggle CLI installed: {result.stdout.strip()}")
        
        # Check for API key
        kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
        if not kaggle_json.exists():
            print("❌ Kaggle API key not found")
            print("   Please download your API key from:")
            print("   https://www.kaggle.com/settings/account")
            print(f"   And place it at: {kaggle_json}")
            return False
        
        print("✓ Kaggle API key found")
        return True
        
    except FileNotFoundError:
        print("❌ Kaggle CLI not installed")
        print("   Install with: pip install kaggle")
        return False


def list_available_datasets():
    """List available Kaggle datasets."""
    print("\nAvailable datasets:\n")
    
    for key, info in KAGGLE_DATASETS.items():
        print(f"  {key}:")
        print(f"    Name: {info['name']}")
        print(f"    Description: {info['description']}")
        print(f"    Size: {info['size']}")
        print(f"    Samples: {info['samples']}\n")


def download_kaggle_dataset(dataset_name, output_dir):
    """Download dataset from Kaggle."""
    print(f"\nDownloading dataset: {dataset_name}")
    print(f"Output directory: {output_dir}\n")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        cmd = ['kaggle', 'datasets', 'download', '-d', dataset_name, '-p', str(output_path)]
        
        print(f"Running: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, check=True)
        
        print("\n✓ Download complete!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Download failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Kaggle CLI not found")
        return False


def extract_zip_files(directory):
    """Extract all zip files in directory."""
    print(f"\nExtracting zip files in {directory}...")
    
    import zipfile
    
    zip_files = list(Path(directory).glob('**/*.zip'))
    
    if not zip_files:
        print("No zip files found")
        return
    
    for zip_file in zip_files:
        print(f"  Extracting {zip_file.name}...")
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(zip_file.parent)
            print(f"  ✓ Extracted")
        except Exception as e:
            print(f"  ❌ Error: {e}")


def organize_respiratory_data(source_dir, target_dir):
    """Organize Respiratory Sound Database into our structure."""
    print(f"\nOrganizing respiratory data from {source_dir}...")
    
    source = Path(source_dir)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    
    # Create target directories
    for disease in ['Healthy', 'Cold Cough', 'COVID-19', 'Asthma', 'Bronchitis', 'Whooping Cough']:
        (target / disease).mkdir(exist_ok=True)
    
    # Look for audio files
    audio_files = list(source.glob('**/*.wav')) + list(source.glob('**/*.mp3'))
    
    if not audio_files:
        print("❌ No audio files found")
        return 0
    
    print(f"Found {len(audio_files)} audio files\n")
    
    organized_count = 0
    
    for audio_file in audio_files:
        filename = audio_file.name.lower()
        
        # Determine destination based on filename
        destination = target / 'Healthy'  # Default
        
        if 'crackle' in filename:
            destination = target / 'Bronchitis'
        elif 'wheeze' in filename or 'asthma' in filename:
            destination = target / 'Asthma'
        elif 'normal' in filename:
            destination = target / 'Healthy'
        elif 'covid' in filename or 'cov' in filename:
            destination = target / 'COVID-19'
        elif 'cold' in filename:
            destination = target / 'Cold Cough'
        elif 'pertussis' in filename or 'whooping' in filename:
            destination = target / 'Whooping Cough'
        
        # Copy file
        try:
            dest_file = destination / audio_file.name
            shutil.copy2(audio_file, dest_file)
            organized_count += 1
            
            if organized_count % 50 == 0:
                print(f"  Organized {organized_count} files...")
                
        except Exception as e:
            print(f"❌ Error copying {audio_file.name}: {e}")
    
    print(f"\n✓ Organized {organized_count} files")
    
    # Print summary
    print("\nDataset summary:")
    for disease in ['Healthy', 'Cold Cough', 'COVID-19', 'Asthma', 'Bronchitis', 'Whooping Cough']:
        disease_dir = target / disease
        count = len(list(disease_dir.glob('*.*')))
        print(f"  {disease}: {count} files")
    
    return organized_count


def main():
    parser = argparse.ArgumentParser(
        description="Download and organize Kaggle respiratory sound datasets"
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available datasets'
    )
    parser.add_argument(
        '--dataset-name',
        type=str,
        default='vbookshelf/respiratory-sound-database',
        help='Kaggle dataset name or key (default: respiratory)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./respiratory_data_raw',
        help='Output directory for downloaded files'
    )
    parser.add_argument(
        '--organize-to',
        type=str,
        default='./audio_data',
        help='Directory to organize files into (default: audio_data)'
    )
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Skip download and only organize existing files'
    )
    parser.add_argument(
        '--extract-only',
        action='store_true',
        help='Extract zip files only'
    )
    
    args = parser.parse_args()
    
    # List datasets
    if args.list:
        list_available_datasets()
        return
    
    # Map dataset key to name if needed
    dataset_name = args.dataset_name
    if dataset_name in KAGGLE_DATASETS:
        dataset_name = KAGGLE_DATASETS[dataset_name]['name']
    
    # Check Kaggle setup
    if not args.skip_download and not args.extract_only:
        if not check_kaggle_setup():
            sys.exit(1)
    
    # Download dataset
    if not args.skip_download and not args.extract_only:
        if not download_kaggle_dataset(dataset_name, args.output):
            sys.exit(1)
    
    # Extract zip files
    if not args.skip_download or args.extract_only:
        extract_zip_files(args.output)
    
    # Organize files
    organized = organize_respiratory_data(args.output, args.organize_to)
    
    if organized > 0:
        print(f"\n✓ Successfully organized {organized} audio files!")
        print(f"✓ Data ready at: {args.organize_to}")
        print(f"\nYou can now train the model with:")
        print(f"  python train.py --audio-dir {args.organize_to}")
    else:
        print("\n❌ No files were organized")
        sys.exit(1)


if __name__ == "__main__":
    main()

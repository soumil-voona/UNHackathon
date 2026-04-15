"""
Kagglehub Dataset Downloader - Simple and Modern
Downloads and organizes Kaggle datasets using kagglehub.

This is simpler than the Kaggle CLI and doesn't require manual API key setup!

Installation:
    pip install kagglehub

Usage:
    python download_kagglehub.py
    python download_kagglehub.py --dataset "vbookshelf/respiratory-sound-database"
    python download_kagglehub.py --organize-to "./my_audio_data"
"""

import os
import sys
import argparse
import random
from pathlib import Path
import shutil

# Available datasets
DATASETS = [
    "vbookshelf/respiratory-sound-database",
    "andrewmvd/covid19-cough-audio-classification",
    "ruchikashirsath/tb-audio"
]

# Maximum number of files to keep from each dataset
MAX_FILES_PER_DATASET = {
    "vbookshelf/respiratory-sound-database": 999999,  # Keep all
    "andrewmvd/covid19-cough-audio-classification": 999999,  # Keep all
    "ruchikashirsath/tb-audio": 1000  # Limit TB to 1000 files
}


def check_kagglehub():
    """Check if kagglehub is installed."""
    print("Checking kagglehub installation...")
    try:
        import kagglehub
        print(f"✓ kagglehub is installed")
        return True
    except ImportError:
        print("❌ kagglehub not found")
        print("Install with: pip install kagglehub")
        return False


def reduce_files(source_dir, max_files):
    """Keep only max_files random samples from source directory, delete the rest."""
    if max_files >= 999999:
        return  # Keep all files
    
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    # Find all audio files
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(Path(source_dir).rglob(f"*{ext}"))
    
    print(f"  Found {len(audio_files)} total files")
    
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
    
    print(f"  Reduced to {max_files} files (deleted {deleted_count})")



def download_with_kagglehub(dataset_name):
    """Download dataset using kagglehub."""
    print(f"\n📥 Downloading dataset using kagglehub...")
    print(f"   Dataset: {dataset_name}\n")
    
    try:
        import kagglehub
        
        # Download latest version
        path = kagglehub.dataset_download(dataset_name)
        print(f"✓ Download complete!")
        print(f"✓ Path: {path}\n")
        return path
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


def organize_respiratory_data(source_dir, target_dir):
    """Organize Respiratory Sound Database into our structure."""
    print(f"Organizing respiratory data from {source_dir}...")
    
    source = Path(source_dir)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    
    # Create target directories (includes TB and Pneumonia)
    for disease in ['Healthy', 'Cold Cough', 'COVID-19', 'Asthma', 'Bronchitis', 
                    'Whooping Cough', 'Tuberculosis', 'Pneumonia']:
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
        
        if 'crackle' in filename or 'rales' in filename:
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
        elif 'pneumonia' in filename:
            destination = target / 'Pneumonia'
        elif 'tb' in filename or 'tuberculosis' in filename:
            destination = target / 'Tuberculosis'
        
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
    for disease in ['Healthy', 'Cold Cough', 'COVID-19', 'Asthma', 'Bronchitis', 
                    'Whooping Cough', 'Tuberculosis', 'Pneumonia']:
        disease_dir = target / disease
        count = len(list(disease_dir.glob('*.*')))
        if count > 0:
            print(f"  {disease}: {count} files")
    
    return organized_count


def organize_covid_dataset(source_dir, target_dir):
    """Organize COVID-19 cough audio dataset."""
    print(f"Organizing COVID-19 dataset from {source_dir}...")
    
    source = Path(source_dir)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    
    covid_target = target / 'COVID-19'
    covid_target.mkdir(exist_ok=True)
    
    # Look for audio files
    audio_files = list(source.glob('**/*.wav')) + list(source.glob('**/*.mp3'))
    
    if not audio_files:
        print("❌ No audio files found")
        return 0
    
    print(f"Found {len(audio_files)} audio files\n")
    
    organized_count = 0
    for audio_file in audio_files:
        try:
            dest_file = covid_target / audio_file.name
            shutil.copy2(audio_file, dest_file)
            organized_count += 1
            
            if organized_count % 50 == 0:
                print(f"  Organized {organized_count} files...")
                
        except Exception as e:
            print(f"❌ Error copying {audio_file.name}: {e}")
    
    print(f"\n✓ Organized {organized_count} COVID-19 files")
    return organized_count


def organize_tb_dataset(source_dir, target_dir):
    """Organize TB audio dataset."""
    print(f"Organizing TB dataset from {source_dir}...")
    
    source = Path(source_dir)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    
    tb_target = target / 'Tuberculosis'
    tb_target.mkdir(exist_ok=True)
    
    # Look for audio files
    audio_files = list(source.glob('**/*.wav')) + list(source.glob('**/*.mp3'))
    
    if not audio_files:
        print("❌ No audio files found")
        return 0
    
    print(f"Found {len(audio_files)} audio files\n")
    
    organized_count = 0
    for audio_file in audio_files:
        try:
            dest_file = tb_target / audio_file.name
            shutil.copy2(audio_file, dest_file)
            organized_count += 1
            
            if organized_count % 50 == 0:
                print(f"  Organized {organized_count} files...")
                
        except Exception as e:
            print(f"❌ Error copying {audio_file.name}: {e}")
    
    print(f"\n✓ Organized {organized_count} TB files")
    return organized_count


def main():
    parser = argparse.ArgumentParser(
        description="Download and organize Kaggle datasets using kagglehub"
    )
    parser.add_argument(
        '--dataset',
        type=str,
        default='all',
        choices=['all', 'respiratory', 'covid', 'tb'],
        help='Which dataset to download (default: all)'
    )
    parser.add_argument(
        '--organize-to',
        type=str,
        default='./audio_data',
        help='Directory to organize files into (default: audio_data)'
    )
    parser.add_argument(
        '--skip-organize',
        action='store_true',
        help='Skip organizing files, just download'
    )
    
    args = parser.parse_args()
    
    # Check kagglehub
    if not check_kagglehub():
        sys.exit(1)
    
    # Map dataset choices to slugs
    dataset_map = {
        'respiratory': 'vbookshelf/respiratory-sound-database',
        'covid': 'andrewmvd/covid19-cough-audio-classification',
        'tb': 'ruchikashirsath/tb-audio'
    }
    
    # Determine which datasets to download
    if args.dataset == 'all':
        datasets_to_download = DATASETS
    else:
        datasets_to_download = [dataset_map[args.dataset]]
    
    total_organized = 0
    
    for dataset_slug in datasets_to_download:
        print("\n" + "="*60)
        print(f"Processing: {dataset_slug}")
        print("="*60)
        
        # Download dataset
        download_path = download_with_kagglehub(dataset_slug)
        
        if not download_path:
            print(f"⚠️  Skipping organization for {dataset_slug}")
            continue
        
        # Reduce dataset size if needed
        max_files = MAX_FILES_PER_DATASET.get(dataset_slug, 999999)
        print(f"  Limiting to {max_files} files...")
        reduce_files(download_path, max_files)
        
        # Organize files based on dataset type
        if not args.skip_organize:
            organized = 0
            
            if 'respiratory-sound' in dataset_slug:
                organized = organize_respiratory_data(download_path, args.organize_to)
            elif 'covid' in dataset_slug:
                organized = organize_covid_dataset(download_path, args.organize_to)
            elif 'tb-audio' in dataset_slug:
                organized = organize_tb_dataset(download_path, args.organize_to)
            
            total_organized += organized
    
    print("\n" + "="*60)
    if total_organized > 0:
        print(f"✓ Successfully organized {total_organized} total audio files!")
        print(f"✓ Data ready at: {args.organize_to}")
        print(f"\nYou can now train the model with:")
        print(f"  python train.py --audio-dir {args.organize_to}")
    else:
        print("❌ No files were organized")
        sys.exit(1)


if __name__ == "__main__":
    main()

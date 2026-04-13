"""
Kagglehub Dataset Downloader - Simple and Modern
Downloads and organizes Kaggle datasets using kagglehub.

This is simpler than the Kaggle CLI and doesn't require manual API key setup!

Installation:
    pip install kagglehub

Usage:
    python download_kagglehub.py
    
    # With options
    python download_kagglehub.py --dataset "vbookshelf/respiratory-sound-database"
    python download_kagglehub.py --organize-to "./my_audio_data"
"""

import os
import sys
import argparse
from pathlib import Path
import shutil


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
        if count > 0:
            print(f"  {disease}: {count} files")
    
    return organized_count


def main():
    parser = argparse.ArgumentParser(
        description="Download and organize Kaggle datasets using kagglehub"
    )
    parser.add_argument(
        '--dataset',
        type=str,
        default='vbookshelf/respiratory-sound-database',
        help='Kaggle dataset name (default: respiratory-sound-database)'
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
    
    # Download dataset
    download_path = download_with_kagglehub(args.dataset)
    
    if not download_path:
        sys.exit(1)
    
    # Organize files
    if not args.skip_organize:
        organized = organize_respiratory_data(download_path, args.organize_to)
        
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

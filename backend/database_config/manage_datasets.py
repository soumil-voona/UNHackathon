"""
Batch Dataset Manager - Download and combine multiple datasets.
Allows you to combine multiple Kaggle datasets into one training dataset.

Usage:
    python manage_datasets.py --combine-all
    python manage_datasets.py --list-datasets
    python manage_datasets.py --combine respiratory coughvid
"""

import argparse
import subprocess
from pathlib import Path
import shutil
from collections import defaultdict


# Available datasets
DATASETS = {
    'respiratory': {
        'kaggle_name': 'vbookshelf/respiratory-sound-database',
        'description': 'Respiratory Sound Database - 920+ recordings',
        'classes': {
            'normal': 'Healthy',
            'crackles': 'Bronchitis',
            'wheezes': 'Asthma',
            'both': 'Bronchitis',
        }
    },
    'coughvid': {
        'kaggle_name': 'vbookshelf/coughvid-a-large-scale-open-source-cough-audio-dataset',
        'description': 'COUGHVID - 25,000+ cough recordings',
        'classes': {
            'covid': 'COVID-19',
            'healthy': 'Healthy',
            'cold': 'Cold Cough',
            'asthma': 'Asthma',
        }
    },
    'urban-sound': {
        'kaggle_name': 'pavansanagapati/urban-sound-classification',
        'description': 'Urban Sound Classification - 8,732 samples',
        'classes': {}
    },
}

TARGET_CLASSES = [
    'Healthy',
    'Cold Cough',
    'COVID-19',
    'Asthma',
    'Bronchitis',
    'Whooping Cough'
]


def list_available_datasets():
    """List all available datasets."""
    print("\n📊 Available Datasets:\n")
    
    for key, info in DATASETS.items():
        print(f"  {key}:")
        print(f"    Description: {info['description']}")
        print(f"    Kaggle: {info['kaggle_name']}\n")


def download_dataset(dataset_key, output_dir):
    """Download a single dataset."""
    if dataset_key not in DATASETS:
        print(f"❌ Unknown dataset: {dataset_key}")
        return False
    
    dataset_info = DATASETS[dataset_key]
    kaggle_name = dataset_info['kaggle_name']
    
    print(f"\n📥 Downloading {dataset_key}...")
    print(f"   Source: {kaggle_name}")
    
    try:
        cmd = [
            'kaggle', 'datasets', 'download',
            '-d', kaggle_name,
            '-p', str(output_dir),
            '--unzip'
        ]
        
        result = subprocess.run(cmd, check=True)
        print(f"   ✓ Download complete")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Download failed: {e}")
        return False


def combine_datasets(dataset_keys, output_dir='audio_data_combined'):
    """Combine multiple datasets into one directory."""
    print(f"\n🔄 Combining datasets: {', '.join(dataset_keys)}")
    print(f"   Output: {output_dir}\n")
    
    output_path = Path(output_dir)
    
    # Create target class directories
    for disease_class in TARGET_CLASSES:
        (output_path / disease_class).mkdir(parents=True, exist_ok=True)
    
    total_files = 0
    class_counts = defaultdict(int)
    
    for dataset_key in dataset_keys:
        if dataset_key not in DATASETS:
            print(f"   ⚠ Unknown dataset: {dataset_key}, skipping")
            continue
        
        dataset_dir = Path(f"respiratory_data_raw_{dataset_key}")
        
        if not dataset_dir.exists():
            print(f"   ⚠ Dataset directory not found: {dataset_dir}")
            print(f"      Run: python download_dataset.py --dataset-name {dataset_key}")
            continue
        
        print(f"   Processing {dataset_key}...")
        
        # Find all audio files
        audio_files = list(dataset_dir.glob('**/*.wav')) + list(dataset_dir.glob('**/*.mp3'))
        
        for audio_file in audio_files:
            filename = audio_file.name.lower()
            
            # Determine destination class
            destination_class = 'Healthy'  # Default
            
            # Check file name for clues
            if 'crackle' in filename or 'rales' in filename:
                destination_class = 'Bronchitis'
            elif 'wheeze' in filename:
                destination_class = 'Asthma'
            elif 'covid' in filename or 'cov' in filename:
                destination_class = 'COVID-19'
            elif 'cold' in filename:
                destination_class = 'Cold Cough'
            elif 'pertussis' in filename or 'whooping' in filename:
                destination_class = 'Whooping Cough'
            elif 'normal' in filename or 'healthy' in filename:
                destination_class = 'Healthy'
            
            # Copy file
            try:
                dest_file = output_path / destination_class / audio_file.name
                shutil.copy2(audio_file, dest_file)
                total_files += 1
                class_counts[destination_class] += 1
            except Exception as e:
                print(f"      ⚠ Error copying {audio_file.name}: {e}")
        
        print(f"   ✓ Processed {len(audio_files)} files from {dataset_key}")
    
    # Print summary
    print(f"\n📊 Combined Dataset Summary:")
    print(f"   Total files: {total_files}\n")
    print(f"   Class distribution:")
    
    for disease_class in TARGET_CLASSES:
        count = class_counts[disease_class]
        if count > 0:
            print(f"     {disease_class}: {count} files")
    
    print(f"\n✓ Combined dataset ready at: {output_dir}")
    print(f"\n   Train with: python train.py --audio-dir {output_dir}")


def get_dataset_stats(dataset_dir):
    """Get statistics about a dataset."""
    path = Path(dataset_dir)
    
    if not path.exists():
        print(f"❌ Directory not found: {dataset_dir}")
        return
    
    print(f"\n📊 Dataset Statistics: {dataset_dir}\n")
    
    total = 0
    for disease_class in TARGET_CLASSES:
        class_dir = path / disease_class
        if class_dir.exists():
            count = len(list(class_dir.glob('*.*')))
            total += count
            if count > 0:
                print(f"   {disease_class}: {count} files")
    
    print(f"\n   Total: {total} files")


def download_and_combine(dataset_keys, base_output='./datasets'):
    """Download and combine multiple datasets at once."""
    print("🚀 Download and Combine Mode")
    print(f"   Datasets: {', '.join(dataset_keys)}")
    print(f"   Base directory: {base_output}\n")
    
    base_path = Path(base_output)
    base_path.mkdir(exist_ok=True)
    
    # Download each dataset
    for dataset_key in dataset_keys:
        dataset_output = base_path / f"{dataset_key}_raw"
        dataset_output.mkdir(exist_ok=True)
        
        if not download_dataset(dataset_key, str(dataset_output)):
            print(f"⚠ Failed to download {dataset_key}, continuing...")
    
    # Combine all datasets
    combined_output = base_path / "combined"
    combine_datasets(dataset_keys, str(combined_output))


def main():
    parser = argparse.ArgumentParser(
        description="Batch dataset manager for Cough Classifier"
    )
    parser.add_argument(
        '--list-datasets',
        action='store_true',
        help='List available datasets'
    )
    parser.add_argument(
        '--combine',
        nargs='+',
        help='Combine specific datasets (e.g., --combine respiratory coughvid)'
    )
    parser.add_argument(
        '--combine-all',
        action='store_true',
        help='Download and combine all available datasets'
    )
    parser.add_argument(
        '--download-combine',
        nargs='+',
        help='Download and combine datasets in one step'
    )
    parser.add_argument(
        '--stats',
        type=str,
        help='Show statistics for a dataset directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='audio_data_combined',
        help='Output directory for combined dataset'
    )
    
    args = parser.parse_args()
    
    # List datasets
    if args.list_datasets:
        list_available_datasets()
        return
    
    # Get stats
    if args.stats:
        get_dataset_stats(args.stats)
        return
    
    # Combine all
    if args.combine_all:
        dataset_keys = list(DATASETS.keys())
        download_and_combine(dataset_keys)
        return
    
    # Download and combine
    if args.download_combine:
        download_and_combine(args.download_combine)
        return
    
    # Combine specific datasets
    if args.combine:
        combine_datasets(args.combine, args.output)
        return
    
    # Show help if no arguments
    parser.print_help()


if __name__ == "__main__":
    main()

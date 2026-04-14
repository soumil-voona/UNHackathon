"""
Script to organize and integrate multiple Kaggle datasets for cough classification.

This script handles:
1. vbookshelf/respiratory-sound-database - Maps URTI to "Cold Cough"
2. andrewmvd/covid19-cough-audio-classification - Extracts COVID-19 and Healthy samples
3. ruchikashirsath/tb-audio - Extracts Tuberculosis and Pneumonia samples

Usage:
    python organize_datasets.py --input-dir ./kaggle_datasets --output-dir ./audio_data
"""

import os
import shutil
import argparse
from pathlib import Path
import json
from collections import defaultdict

# Disease class mapping from source datasets to unified classification
DATASET_MAPPINGS = {
    # Respiratory Sound Database mappings
    "respiratory_sound_database": {
        "Healthy": "Healthy",
        "URTI": "Cold Cough",  # Upper Respiratory Tract Infection
        "Asthma": "Asthma",
        "Bronchitis": "Bronchitis",
    },
    # COVID-19 Cough Classification mappings
    "covid19_cough": {
        "covid_19": "COVID-19",
        "healthy": "Healthy",
        "other": "Other",  # We'll skip this category
    },
    # TB Audio dataset mappings
    "tb_audio": {
        "tuberculosis": "Tuberculosis",
        "pneumonia": "Pneumonia",
        "healthy": "Healthy",
    }
}

UNIFIED_CLASSES = {
    "Healthy",
    "Cold Cough",
    "COVID-19",
    "Asthma",
    "Bronchitis",
    "Tuberculosis",
    "Pneumonia"
}


def organize_respiratory_sound_database(source_dir, output_dir):
    """Organize the Respiratory Sound Database."""
    print("\n[1/3] Processing Respiratory Sound Database...")
    
    source_path = Path(source_dir) / "respiratory-sound-database"
    if not source_path.exists():
        print(f"  ⚠ Dataset not found at {source_path}")
        return {"status": "not_found", "count": 0}
    
    organized = defaultdict(list)
    count = 0
    
    # Look for audio files in the dataset directory
    for audio_file in source_path.rglob("*.wav"):
        # Try to determine disease from directory structure
        disease = None
        for dir_part in audio_file.parts:
            for src_disease, unified_disease in DATASET_MAPPINGS["respiratory_sound_database"].items():
                if src_disease.lower() in dir_part.lower():
                    disease = unified_disease
                    break
        
        if disease:
            # Copy file to organized directory
            disease_dir = Path(output_dir) / disease
            disease_dir.mkdir(parents=True, exist_ok=True)
            dest_file = disease_dir / audio_file.name
            try:
                shutil.copy2(audio_file, dest_file)
                organized[disease].append(str(dest_file))
                count += 1
            except Exception as e:
                print(f"  ✗ Error copying {audio_file.name}: {e}")
    
    print(f"  ✓ Organized {count} files from Respiratory Sound Database")
    for disease, files in organized.items():
        print(f"    - {disease}: {len(files)} files")
    
    return {"status": "success", "count": count, "distribution": dict(organized)}


def organize_covid19_cough(source_dir, output_dir):
    """Organize the COVID-19 Cough Classification dataset."""
    print("\n[2/3] Processing COVID-19 Cough Classification...")
    
    source_path = Path(source_dir) / "covid19-cough-audio-classification"
    if not source_path.exists():
        print(f"  ⚠ Dataset not found at {source_path}")
        return {"status": "not_found", "count": 0}
    
    organized = defaultdict(list)
    count = 0
    
    # Look for audio files organized by disease
    for audio_file in source_path.rglob("*.wav"):
        disease = None
        for dir_part in audio_file.parts:
            for src_disease, unified_disease in DATASET_MAPPINGS["covid19_cough"].items():
                if src_disease.lower() in dir_part.lower():
                    disease = unified_disease
                    break
        
        # Skip "Other" category
        if disease and disease != "Other":
            disease_dir = Path(output_dir) / disease
            disease_dir.mkdir(parents=True, exist_ok=True)
            dest_file = disease_dir / audio_file.name
            try:
                shutil.copy2(audio_file, dest_file)
                organized[disease].append(str(dest_file))
                count += 1
            except Exception as e:
                print(f"  ✗ Error copying {audio_file.name}: {e}")
    
    print(f"  ✓ Organized {count} files from COVID-19 dataset")
    for disease, files in organized.items():
        print(f"    - {disease}: {len(files)} files")
    
    return {"status": "success", "count": count, "distribution": dict(organized)}


def organize_tb_audio(source_dir, output_dir):
    """Organize the TB Audio dataset."""
    print("\n[3/3] Processing TB Audio Dataset...")
    
    source_path = Path(source_dir) / "tb-audio"
    if not source_path.exists():
        print(f"  ⚠ Dataset not found at {source_path}")
        return {"status": "not_found", "count": 0}
    
    organized = defaultdict(list)
    count = 0
    
    # Look for audio files organized by disease
    for audio_file in source_path.rglob("*.wav"):
        disease = None
        for dir_part in audio_file.parts:
            for src_disease, unified_disease in DATASET_MAPPINGS["tb_audio"].items():
                if src_disease.lower() in dir_part.lower():
                    disease = unified_disease
                    break
        
        if disease:
            disease_dir = Path(output_dir) / disease
            disease_dir.mkdir(parents=True, exist_ok=True)
            dest_file = disease_dir / audio_file.name
            try:
                shutil.copy2(audio_file, dest_file)
                organized[disease].append(str(dest_file))
                count += 1
            except Exception as e:
                print(f"  ✗ Error copying {audio_file.name}: {e}")
    
    print(f"  ✓ Organized {count} files from TB Audio dataset")
    for disease, files in organized.items():
        print(f"    - {disease}: {len(files)} files")
    
    return {"status": "success", "count": count, "distribution": dict(organized)}


def print_summary(results, output_dir):
    """Print a summary of the organization process."""
    print("\n" + "="*60)
    print("DATASET ORGANIZATION SUMMARY")
    print("="*60)
    
    total_files = sum(r.get("count", 0) for r in results)
    successful = sum(1 for r in results if r.get("status") == "success")
    
    print(f"\n✓ Successfully organized {total_files} files")
    print(f"✓ {successful}/{len(results)} datasets processed")
    print(f"\nOutput directory: {output_dir}")
    
    # Show final distribution
    print("\nFinal Distribution:")
    output_path = Path(output_dir)
    if output_path.exists():
        total_per_class = {}
        for disease_dir in output_path.iterdir():
            if disease_dir.is_dir():
                file_count = len(list(disease_dir.glob("*.wav")))
                total_per_class[disease_dir.name] = file_count
        
        for disease in sorted(UNIFIED_CLASSES):
            count = total_per_class.get(disease, 0)
            bar = "█" * (count // 10) if count > 0 else ""
            print(f"  {disease:20s} {count:4d} files {bar}")
    
    print("\n" + "="*60)
    print("Ready for training! Run: python train.py")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Organize and integrate multiple Kaggle datasets for cough classification"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="./kaggle_datasets",
        help="Directory containing downloaded Kaggle datasets"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./audio_data",
        help="Output directory for organized audio files"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("KAGGLE DATASET ORGANIZATION TOOL")
    print("="*60)
    print(f"Input directory:  {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print("="*60)
    
    # Process each dataset
    results = []
    results.append(organize_respiratory_sound_database(args.input_dir, args.output_dir))
    results.append(organize_covid19_cough(args.input_dir, args.output_dir))
    results.append(organize_tb_audio(args.input_dir, args.output_dir))
    
    # Print summary
    print_summary(results, args.output_dir)


if __name__ == "__main__":
    main()

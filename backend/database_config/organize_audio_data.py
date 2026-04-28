"""
Organize downloaded datasets into the expected audio_data directory structure.
Maps various respiratory datasets to the standardized disease categories.
"""

import os
import shutil
import csv
from pathlib import Path
import json

# Define category mappings
CATEGORY_MAPPINGS = {
    'Healthy': ['Healthy'],
    'Cold Cough': ['URTI', 'LRTI', 'Cold'],
    'COVID-19': ['COVID-19', 'covid-19'],
    'Asthma': ['Asthma'],
    'Bronchitis': ['COPD', 'Bronchiectasis', 'Bronchitis'],
    'Whooping Cough': ['Whooping Cough', 'Pertussis'],
}

AUDIO_EXTENSIONS = {'.wav'}
KAGGLE_CACHE = Path.home() / '.cache' / 'kagglehub' / 'datasets'
OUTPUT_DIR = Path('./audio_data')


def create_output_directories():
    """Create the output directory structure."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    for category in CATEGORY_MAPPINGS.keys():
        (OUTPUT_DIR / category).mkdir(exist_ok=True)
    print(f"Created output directories in {OUTPUT_DIR.absolute()}")


def organize_respiratory_database():
    """Organize respiratory sound database by patient diagnosis."""
    print("\n" + "="*60)
    print("Organizing Respiratory Sound Database...")
    print("="*60)
    
    base_path = KAGGLE_CACHE / 'vbookshelf' / 'respiratory-sound-database' / 'versions' / '2' / 'Respiratory_Sound_Database' / 'Respiratory_Sound_Database'
    
    if not base_path.exists():
        print(f"❌ Respiratory database not found at {base_path}")
        return 0
    
    # Read patient diagnosis
    diagnosis_csv = base_path / 'patient_diagnosis.csv'
    patient_diagnosis = {}
    
    try:
        with open(diagnosis_csv, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    patient_id, diagnosis = row[0], row[1]
                    patient_diagnosis[patient_id] = diagnosis
        print(f"  Loaded diagnoses for {len(patient_diagnosis)} patients")
    except Exception as e:
        print(f"  ❌ Error reading diagnosis CSV: {e}")
        return 0
    
    # Find and copy audio files
    audio_dir = base_path / 'audio_and_txt_files'
    if not audio_dir.exists():
        print(f"  ❌ Audio directory not found")
        return 0
    
    copy_count = 0
    
    for audio_file in audio_dir.rglob('*'):
        if audio_file.suffix.lower() in AUDIO_EXTENSIONS:
            # Extract patient ID from filename (format: patientXXX_...)
            filename = audio_file.stem
            try:
                # Patient ID is typically the first part before underscore
                parts = filename.split('_')
                patient_id = parts[0].replace('patient', '')
                
                if patient_id in patient_diagnosis:
                    diagnosis = patient_diagnosis[patient_id]
                    
                    # Find matching category
                    target_category = None
                    for category, diagnoses in CATEGORY_MAPPINGS.items():
                        if diagnosis in diagnoses:
                            target_category = category
                            break
                    
                    if target_category:
                        dest_dir = OUTPUT_DIR / target_category
                        dest_file = dest_dir / audio_file.name
                        
                        # Avoid duplicate copying
                        if not dest_file.exists():
                            shutil.copy2(audio_file, dest_file)
                            copy_count += 1
                            if copy_count % 50 == 0:
                                print(f"  Copied {copy_count} files...")
                    else:
                        print(f"  ⚠️  No category found for diagnosis: {diagnosis}")
            except Exception as e:
                print(f"  ⚠️  Error processing {audio_file.name}: {e}")
    
    print(f"  ✓ Copied {copy_count} files from respiratory database")
    return copy_count


def organize_covid_dataset():
    """Organize COVID-19 cough audio classification dataset."""
    print("\n" + "="*60)
    print("Organizing COVID-19 Cough Audio Dataset...")
    print("="*60)
    
    base_path = KAGGLE_CACHE / 'andrewmvd' / 'covid19-cough-audio-classification' / 'versions' / '1'
    
    if not base_path.exists():
        print(f"❌ COVID-19 dataset not found at {base_path}")
        return 0
    
    # Read metadata
    metadata_csv = base_path / 'metadata_compiled.csv'
    uuid_status = {}
    
    try:
        with open(metadata_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                uuid = row.get('uuid', '')
                status = row.get('status', '').strip().lower()
                if uuid and status:
                    # Map status to our categories
                    if 'covid' in status.lower():
                        uuid_status[uuid] = 'COVID-19'
                    elif 'healthy' in status.lower():
                        uuid_status[uuid] = 'Healthy'
        
        print(f"  Loaded metadata for {len(uuid_status)} recordings")
    except Exception as e:
        print(f"  ❌ Error reading metadata CSV: {e}")
        # Try without metadata
        uuid_status = {}
    
    # Find and copy audio files
    copy_count = 0
    
    for audio_file in base_path.glob('*'):
        if audio_file.suffix.lower() in AUDIO_EXTENSIONS:
            uuid = audio_file.stem
            
            if uuid in uuid_status:
                target_category = uuid_status[uuid]
                dest_dir = OUTPUT_DIR / target_category
                dest_file = dest_dir / audio_file.name
                
                if not dest_file.exists():
                    shutil.copy2(audio_file, dest_file)
                    copy_count += 1
                    if copy_count % 50 == 0:
                        print(f"  Copied {copy_count} files...")
            elif not uuid_status:  # If we couldn't read metadata, assume healthy
                dest_dir = OUTPUT_DIR / 'Healthy'
                dest_file = dest_dir / audio_file.name
                if not dest_file.exists():
                    shutil.copy2(audio_file, dest_file)
                    copy_count += 1
    
    print(f"  ✓ Copied {copy_count} files from COVID-19 dataset")
    return copy_count


def organize_tb_dataset():
    """Organize tuberculosis audio dataset."""
    print("\n" + "="*60)
    print("Organizing TB Audio Dataset...")
    print("="*60)
    
    base_path = KAGGLE_CACHE / 'ruchikashirsath' / 'tb-audio' / 'versions' / '1'
    
    if not base_path.exists():
        print(f"❌ TB dataset not found at {base_path}")
        return 0
    
    # TB audio typically includes respiratory sounds - categorize as "Cold Cough" or create separate
    # For now, we'll put TB samples in "Bronchitis" category as they're respiratory infections
    target_category = 'Bronchitis'
    dest_dir = OUTPUT_DIR / target_category
    
    copy_count = 0
    
    for audio_file in base_path.rglob('*'):
        if audio_file.suffix.lower() in AUDIO_EXTENSIONS:
            dest_file = dest_dir / audio_file.name
            
            if not dest_file.exists():
                try:
                    shutil.copy2(audio_file, dest_file)
                    copy_count += 1
                    if copy_count % 100 == 0:
                        print(f"  Copied {copy_count} files...")
                except Exception as e:
                    print(f"  ⚠️  Error copying {audio_file.name}: {e}")
    
    print(f"  ✓ Copied {copy_count} files from TB dataset")
    return copy_count


def print_summary():
    """Print summary of organized data."""
    print("\n" + "="*60)
    print("Summary of Organized Audio Data")
    print("="*60)
    
    total_files = 0
    for category in CATEGORY_MAPPINGS.keys():
        category_dir = OUTPUT_DIR / category
        file_count = len(list(category_dir.glob('*.*')))
        total_files += file_count
        print(f"  {category:20s}: {file_count:5d} files")
    
    print(f"\n  {'TOTAL':20s}: {total_files:5d} files")
    print(f"\nAudio data ready at: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    print("\n🎵 Organizing Downloaded Datasets into Audio Categories...")
    
    create_output_directories()
    
    total_copied = 0
    total_copied += organize_respiratory_database()
    total_copied += organize_covid_dataset()
    total_copied += organize_tb_dataset()
    
    print_summary()
    
    print(f"\n✅ Organization complete! ({total_copied} total files copied)")

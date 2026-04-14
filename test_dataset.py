#!/usr/bin/env python3
"""Debug script to test dataset loading."""

import sys
from pathlib import Path
from main import CoughAudioDataset, DISEASE_CLASSES

print("DISEASE_CLASSES mapping:")
for class_idx, class_name in DISEASE_CLASSES.items():
    print(f"  {class_idx}: {class_name}")

audio_dir = "audio_data"
print(f"\nChecking audio_dir: {audio_dir}")
print(f"Path exists: {Path(audio_dir).exists()}")

print("\nLooking for category directories:")
for class_idx, class_name in DISEASE_CLASSES.items():
    class_dir = Path(audio_dir) / class_name
    exists = class_dir.exists()
    if exists:
        audio_files = list(class_dir.glob("*.wav")) + list(class_dir.glob("*.mp3"))
        count = len(audio_files)
        print(f"  {class_name}: {exists} - {count} files")
    else:
        print(f"  {class_name}: {exists} - MISSING DIRECTORY")

print("\nLoading dataset...")
try:
    dataset = CoughAudioDataset(audio_dir)
    print(f"✓ Dataset loaded successfully!")
    print(f"  Total samples: {len(dataset)}")
    print(f"  Audio files: {len(dataset.audio_files)}")
    print(f"  Labels: {len(dataset.labels)}")
    
    if len(dataset) > 0:
        print(f"\nSample info:")
        print(f"  First audio file: {dataset.audio_files[0]}")
        print(f"  First label: {dataset.labels[0]}")
        print(f"  Label mapping: {DISEASE_CLASSES[dataset.labels[0]]}")
    else:
        print("\n✗ ERROR: Dataset is empty!")
        
except Exception as e:
    print(f"✗ ERROR loading dataset: {e}")
    import traceback
    traceback.print_exc()

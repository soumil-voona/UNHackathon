#!/usr/bin/env python3
"""Test loading a batch of data from the dataset."""

import torch
from torch.utils.data import DataLoader
from main import CoughAudioDataset

print("Loading dataset...")
dataset = CoughAudioDataset("audio_data")
print(f"✓ Dataset loaded: {len(dataset)} samples")

print("\nCreating DataLoader...")
dataloader = DataLoader(dataset, batch_size=4, shuffle=False, num_workers=0)
print(f"✓ DataLoader created")

print("\nLoading first batch...")
try:
    for batch_idx, (mel_specs, labels) in enumerate(dataloader):
        print(f"✓ Batch {batch_idx} loaded successfully!")
        print(f"  Mel-spectrogram shape: {mel_specs.shape}")  # Should be [batch, channels, freq, time]
        print(f"  Labels shape: {labels.shape}")
        print(f"  Labels: {labels.tolist()}")
        if batch_idx == 0:  # Just test first batch
            break
except Exception as e:
    print(f"✗ ERROR loading batch: {e}")
    import traceback
    traceback.print_exc()

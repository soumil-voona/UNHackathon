"""
Training script for the Cough Classifier model.
This script handles data loading, model training, and checkpoint management.
"""

import torch
import argparse
import os
from pathlib import Path
from torch.utils.data import DataLoader, WeightedRandomSampler, Subset
from sklearn.model_selection import train_test_split
from backend.main import (
    CoughClassifier,
    CoughClassifierTrainer,
    CoughAudioDataset,
    NUM_CLASSES,
    compute_class_weights,
    extract_labels_from_dataset,
)


def train_model(
    audio_dir,
    batch_size=16,
    epochs=10,
    learning_rate=0.001,
    train_split=0.8,
    output_model="cough_classifier.pt",
    best_model=None,
    resume_from=None,
    max_samples=None,
    max_samples_per_class=None,
    num_workers=0,
    torch_threads=None,
    torch_interop_threads=None,
):
    """
    Train the cough classifier model.
    
    Args:
        audio_dir: Path to directory containing organized audio data
        batch_size: Batch size for training
        epochs: Number of training epochs
        learning_rate: Initial learning rate
        train_split: Fraction of data to use for training
        output_model: Path to save the trained model
        best_model: Optional path for the best validation checkpoint
        resume_from: Optional checkpoint path to continue training from
    """
    
    # Check if audio directory exists
    audio_path = Path(audio_dir)
    if not audio_path.exists():
        print(f"Error: Audio directory '{audio_dir}' not found!")
        print("Please create an 'audio_data' directory with subdirectories for each disease class:")
        print("  - Healthy/")
        print("  - COVID-19/")
        print("  - Bronchitis/")
        print("  - Tuberculosis/")
        return
    
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    if torch_threads is not None:
        torch.set_num_threads(torch_threads)
        print(f"Torch intra-op threads: {torch_threads}")

    if torch_interop_threads is not None:
        torch.set_num_interop_threads(torch_interop_threads)
        print(f"Torch inter-op threads: {torch_interop_threads}")
    
    # Load dataset (no augmentation yet)
    print(f"\nLoading dataset from '{audio_dir}'...")
    dataset = CoughAudioDataset(
        audio_dir,
        max_samples=max_samples,
        max_samples_per_class=max_samples_per_class,
        augment=False,
    )
    print(f"Total samples: {len(dataset)}")
    
    if len(dataset) == 0:
        print("Error: No audio files found in the directory!")
        return
    
    # Split into train and validation with stratification when possible.
    all_labels = extract_labels_from_dataset(dataset)
    all_indices = list(range(len(dataset)))

    try:
        train_indices, val_indices = train_test_split(
            all_indices,
            train_size=train_split,
            random_state=42,
            shuffle=True,
            stratify=all_labels,
        )
        # Create training dataset WITH augmentation
        train_dataset = CoughAudioDataset(
            audio_dir,
            max_samples=max_samples,
            max_samples_per_class=max_samples_per_class,
            augment=True,
        )
        train_dataset = Subset(train_dataset, train_indices)
        val_dataset = Subset(dataset, val_indices)
    except ValueError:
        # Fallback when stratification is not feasible (e.g., extremely tiny classes).
        split_idx = int(train_split * len(all_indices))
        rng = torch.Generator().manual_seed(42)
        perm = torch.randperm(len(all_indices), generator=rng).tolist()
        # Create training dataset WITH augmentation
        train_dataset = CoughAudioDataset(
            audio_dir,
            max_samples=max_samples,
            max_samples_per_class=max_samples_per_class,
            augment=True,
        )
        train_dataset = Subset(train_dataset, perm[:split_idx])
        val_dataset = Subset(dataset, perm[split_idx:])
    
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    
    # Create a balanced sampler for the training split.
    train_labels = extract_labels_from_dataset(train_dataset)
    class_weights = compute_class_weights(train_labels, NUM_CLASSES)
    sample_weights = torch.tensor([class_weights[label].item() for label in train_labels], dtype=torch.double)
    train_sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True,
    )

    worker_count = max(0, int(num_workers))
    persistent_workers = worker_count > 0
    if worker_count > 0:
        print(f"DataLoader workers: {worker_count}")

    # Create dataloaders
    loader_kwargs = {
        "batch_size": batch_size,
        "num_workers": worker_count,
        "persistent_workers": persistent_workers,
    }
    if worker_count > 0:
        loader_kwargs["prefetch_factor"] = 4

    train_loader = DataLoader(train_dataset, sampler=train_sampler, **loader_kwargs)
    val_loader = DataLoader(val_dataset, shuffle=False, **loader_kwargs)
    
    # Initialize model and trainer
    model = CoughClassifier(num_classes=NUM_CLASSES)
    trainer = CoughClassifierTrainer(model, device=device, learning_rate=learning_rate)
    if resume_from:
        resume_path = Path(resume_from)
        if not resume_path.exists():
            print(f"Error: resume checkpoint '{resume_from}' not found!")
            return
        trainer.load_model(str(resume_path))
        print(f"Resuming training from '{resume_from}'")
    
    # Train the model
    print(f"\nStarting training for {epochs} epochs...")
    print(f"Batch size: {batch_size}")
    print(f"Learning rate: {learning_rate}")
    trainer.train(train_loader, val_loader, epochs=epochs, best_model_path=best_model)
    
    # Save the final model
    trainer.save_model(output_model)
    print(f"\nTraining complete! Model saved to '{output_model}'")


def main():
    parser = argparse.ArgumentParser(
        description="Train the Cough Classifier model"
    )
    parser.add_argument(
        "--audio-dir",
        type=str,
        default="audio_data",
        help="Path to directory containing organized audio data (default: audio_data)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size for training (default: 16)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs (default: 100)"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.0001,
        help="Initial learning rate (default: 0.0001)"
    )
    parser.add_argument(
        "--train-split",
        type=float,
        default=0.8,
        help="Fraction of data to use for training (default: 0.8)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="cough_classifier.pt",
        help="Path to save the trained model (default: cough_classifier.pt)"
    )
    parser.add_argument(
        "--best-output",
        type=str,
        default=None,
        help="Optional path to save the best validation checkpoint without replacing the inference model"
    )
    parser.add_argument(
        "--resume-from",
        type=str,
        default=None,
        help="Optional checkpoint path to continue training from"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=0,
        help="Maximum number of samples to use for training (default: 0, meaning all samples)"
    )
    parser.add_argument(
        "--max-samples-per-class",
        type=int,
        default=0,
        help="Maximum number of samples to keep per class before splitting (default: 0, meaning no per-class cap)"
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=max(0, min((os.cpu_count() or 1) - 1, 8)),
        help="Number of DataLoader worker processes (default: min(cpu_count-1, 8))"
    )
    parser.add_argument(
        "--torch-threads",
        type=int,
        default=os.cpu_count() or 1,
        help="Torch intra-op thread count (default: cpu_count)"
    )
    parser.add_argument(
        "--torch-interop-threads",
        type=int,
        default=1,
        help="Torch inter-op thread count (default: 1)"
    )
    
    args = parser.parse_args()
    
    train_model(
        audio_dir=args.audio_dir,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        train_split=args.train_split,
        output_model=args.output,
        best_model=args.best_output,
        resume_from=args.resume_from,
        max_samples=args.max_samples if args.max_samples > 0 else None,
        max_samples_per_class=args.max_samples_per_class if args.max_samples_per_class > 0 else None,
        num_workers=args.num_workers,
        torch_threads=args.torch_threads,
        torch_interop_threads=args.torch_interop_threads,
    )


if __name__ == "__main__":
    main()

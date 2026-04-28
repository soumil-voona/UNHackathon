"""
Training script for the Cough Classifier model.
This script handles data loading, model training, and checkpoint management.
"""

import torch
import argparse
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
    epochs=50,
    learning_rate=0.001,
    train_split=0.8,
    output_model="cough_classifier.pt",
    max_samples=None
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
    """
    
    # Check if audio directory exists
    audio_path = Path(audio_dir)
    if not audio_path.exists():
        print(f"Error: Audio directory '{audio_dir}' not found!")
        print("Please create an 'audio_data' directory with subdirectories for each disease class:")
        print("  - Healthy/")
        print("  - Cold Cough/")
        print("  - COVID-19/")
        print("  - Asthma/")
        print("  - Bronchitis/")
        print("  - Whooping Cough/")
        return
    
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load dataset
    print(f"\nLoading dataset from '{audio_dir}'...")
    dataset = CoughAudioDataset(audio_dir, max_samples=max_samples)
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
        train_dataset = Subset(dataset, train_indices)
        val_dataset = Subset(dataset, val_indices)
    except ValueError:
        # Fallback when stratification is not feasible (e.g., extremely tiny classes).
        split_idx = int(train_split * len(all_indices))
        rng = torch.Generator().manual_seed(42)
        perm = torch.randperm(len(all_indices), generator=rng).tolist()
        train_dataset = Subset(dataset, perm[:split_idx])
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

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=train_sampler, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Initialize model and trainer
    model = CoughClassifier(num_classes=NUM_CLASSES)
    trainer = CoughClassifierTrainer(model, device=device, learning_rate=learning_rate)
    
    # Train the model
    print(f"\nStarting training for {epochs} epochs...")
    print(f"Batch size: {batch_size}")
    print(f"Learning rate: {learning_rate}")
    trainer.train(train_loader, val_loader, epochs=epochs)
    
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
        default=10,
        help="Number of training epochs (default: 10)"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.001,
        help="Initial learning rate (default: 0.001)"
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
        "--max-samples",
        type=int,
        default=0,
        help="Maximum number of samples to use for training (default: 0, meaning all samples)"
    )
    
    args = parser.parse_args()
    
    train_model(
        audio_dir=args.audio_dir,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        train_split=args.train_split,
        output_model=args.output,
        max_samples=args.max_samples if args.max_samples > 0 else None
    )


if __name__ == "__main__":
    main()

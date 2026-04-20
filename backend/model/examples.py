"""
Example usage of the Cough Classifier model.
This script demonstrates how to use all the major components.
"""

import torch
from pathlib import Path
from backend.main import CoughClassifier, CoughClassifierTrainer, CoughAudioDataset, NUM_CLASSES, DISEASE_CLASSES
from torch.utils.data import DataLoader, random_split


def example_1_simple_prediction():
    """
    Example 1: Make a simple prediction on a single audio file.
    """
    print("="*60)
    print("Example 1: Simple Prediction")
    print("="*60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CoughClassifier(num_classes=NUM_CLASSES)
    trainer = CoughClassifierTrainer(model, device=device)
    
    # Check if model exists
    model_path = "cough_classifier.pt"
    if Path(model_path).exists():
        trainer.load_model(model_path)
        
        # Make prediction
        audio_file = "path/to/your/audio.wav"
        if Path(audio_file).exists():
            disease, confidence, probs = trainer.predict(audio_file)
            
            print(f"\nAudio: {audio_file}")
            print(f"Predicted Disease: {disease}")
            print(f"Confidence: {confidence:.2%}\n")
            print("All Probabilities:")
            for disease_name, prob in probs.items():
                print(f"  {disease_name}: {prob:.2%}")
        else:
            print(f"Audio file not found: {audio_file}")
    else:
        print(f"Model file not found: {model_path}")
        print("Please train the model first using train.py")


def example_2_batch_prediction():
    """
    Example 2: Classify all audio files in a directory.
    """
    print("\n" + "="*60)
    print("Example 2: Batch Prediction")
    print("="*60)
    
    from backend.inference import CoughInference
    
    inference = CoughInference(model_path="cough_classifier.pt")
    results = inference.classify_multiple("test_audio_directory/")
    inference.save_results(results, "batch_predictions.json")
    
    print(f"\nProcessed {len(results)} files")


def example_3_training():
    """
    Example 3: Train the model from scratch.
    """
    print("\n" + "="*60)
    print("Example 3: Training the Model")
    print("="*60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    audio_dir = "audio_data"
    
    if not Path(audio_dir).exists():
        print(f"Audio directory '{audio_dir}' not found!")
        print("\nPlease organize your audio files in the following structure:")
        print("audio_data/")
        for disease in DISEASE_CLASSES.values():
            print(f"  ├── {disease}/")
            print(f"      └── *.wav (or *.mp3)")
        return
    
    # Load dataset
    print(f"\nLoading dataset from '{audio_dir}'...")
    dataset = CoughAudioDataset(audio_dir)
    print(f"Total samples: {len(dataset)}")
    
    if len(dataset) == 0:
        print("No audio files found!")
        return
    
    # Split data
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    # Initialize model
    model = CoughClassifier(num_classes=NUM_CLASSES)
    trainer = CoughClassifierTrainer(model, device=device, learning_rate=0.001)
    
    # Train
    print(f"\nTraining for 50 epochs...")
    print(f"Training samples: {train_size}")
    print(f"Validation samples: {val_size}")
    trainer.train(train_loader, val_loader, epochs=50)
    
    # Save model
    trainer.save_model("cough_classifier.pt")
    print("\nTraining complete!")


def example_4_model_info():
    """
    Example 4: Display model information.
    """
    print("\n" + "="*60)
    print("Example 4: Model Information")
    print("="*60)
    
    model = CoughClassifier(num_classes=NUM_CLASSES)
    
    print("\nModel Architecture:")
    print(model)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"\nTotal Parameters: {total_params:,}")
    print(f"Trainable Parameters: {trainable_params:,}")
    
    print(f"\nDisease Classes ({NUM_CLASSES}):")
    for idx, disease in DISEASE_CLASSES.items():
        print(f"  {idx}: {disease}")


def example_5_transfer_learning():
    """
    Example 5: Fine-tune a pre-trained model.
    """
    print("\n" + "="*60)
    print("Example 5: Transfer Learning (Fine-tuning)")
    print("="*60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load pre-trained model
    model = CoughClassifier(num_classes=NUM_CLASSES)
    model_path = "cough_classifier.pt"
    
    if Path(model_path).exists():
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"Loaded pre-trained model from {model_path}")
    else:
        print(f"Pre-trained model not found: {model_path}")
        return
    
    # Freeze earlier layers
    for param in model.conv1.parameters():
        param.requires_grad = False
    for param in model.conv2.parameters():
        param.requires_grad = False
    
    print("\nFroze convolutional layers 1-2")
    print("Trainable parameters:")
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(f"  {name}")
    
    # Now you can train with a smaller learning rate on remaining layers
    trainer = CoughClassifierTrainer(model, device=device, learning_rate=0.0001)
    print("\nModel ready for fine-tuning with learning rate: 0.0001")


def main():
    """Run examples."""
    print("\n" + "="*60)
    print("Cough Classifier - Usage Examples")
    print("="*60)
    
    print("\nAvailable examples:")
    print("1. Simple Prediction")
    print("2. Batch Prediction")
    print("3. Training")
    print("4. Model Information")
    print("5. Transfer Learning (Fine-tuning)")
    
    choice = input("\nSelect an example (1-5) or 'all' to run all: ").strip().lower()
    
    if choice == '1':
        example_1_simple_prediction()
    elif choice == '2':
        example_2_batch_prediction()
    elif choice == '3':
        example_3_training()
    elif choice == '4':
        example_4_model_info()
    elif choice == '5':
        example_5_transfer_learning()
    elif choice == 'all':
        example_1_simple_prediction()
        example_2_batch_prediction()
        example_4_model_info()
        example_5_transfer_learning()
        print("\n" + "="*60)
        print("(Skipped Example 3 - requires training data)")
        print("="*60)
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()

# Cough-Based Health Issue Classifier

A PyTorch-based deep learning model that classifies cough audio recordings to identify potential health issues including COVID-19, cold cough, asthma, bronchitis, whooping cough, or healthy status.

## Features

- **CNN Architecture**: Convolutional Neural Network optimized for audio spectrogram analysis
- **Mel-Spectrogram Processing**: Converts raw audio to mel-spectrograms for feature extraction
- **Multi-Class Classification**: Classifies coughs into 6 categories:
  - Healthy
  - Cold Cough
  - COVID-19
  - Asthma
  - Bronchitis
  - Whooping Cough
- **Data Augmentation & Normalization**: Automatic audio preprocessing and normalization
- **Early Stopping**: Prevents overfitting with patience-based early stopping
- **GPU Support**: Automatically uses GPU if available

## Installation

1. Clone the repository:
```bash
cd UNHackathon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
UNHackathon/
├── main.py                      # Main model implementation
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── audio_data/                  # Training data directory (to be created)
    ├── Healthy/
    │   └── *.wav (or *.mp3)
    ├── Cold Cough/
    │   └── *.wav (or *.mp3)
    ├── COVID-19/
    │   └── *.wav (or *.mp3)
    ├── Asthma/
    │   └── *.wav (or *.mp3)
    ├── Bronchitis/
    │   └── *.wav (or *.mp3)
    └── Whooping Cough/
        └── *.wav (or *.mp3)
```

## Model Architecture

### CoughClassifier
- **Input**: Mel-spectrogram (1 channel, 64 mel-bins)
- **Convolutional Layers**: 4 layers with batch normalization and max pooling
- **Fully Connected Layers**: 3 layers with dropout regularization
- **Output**: 6-class probability distribution

### Key Components

1. **CoughAudioDataset**: Custom PyTorch Dataset class
   - Loads audio files from organized directory structure
   - Converts audio to mel-spectrograms
   - Normalizes duration to 3 seconds
   - Applies normalization

2. **CoughClassifier**: Neural network model
   - 4 convolutional blocks (32 → 64 → 128 → 256 filters)
   - Batch normalization for stable training
   - Dropout layers to prevent overfitting
   - Adaptive average pooling for variable input sizes

3. **CoughClassifierTrainer**: Training and inference wrapper
   - Handles training loop with validation
   - Implements early stopping
   - Learning rate scheduling
   - Model persistence (save/load)
   - Single prediction inference

## Usage

### Preparing Training Data

Organize your cough audio files in the following structure:
```
audio_data/
├── Healthy/
│   ├── healthy_cough_001.wav
│   ├── healthy_cough_002.wav
│   └── ...
├── Cold Cough/
│   ├── cold_cough_001.wav
│   └── ...
├── COVID-19/
├── Asthma/
├── Bronchitis/
└── Whooping Cough/
```

Supported formats: `.wav`, `.mp3`

### Training the Model

```python
from main import CoughClassifier, CoughClassifierTrainer, CoughAudioDataset
import torch
from torch.utils.data import DataLoader, random_split

# Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CoughClassifier(num_classes=6)
trainer = CoughClassifierTrainer(model, device=device, learning_rate=0.001)

# Load dataset
dataset = CoughAudioDataset("audio_data")
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

# Train
trainer.train(train_loader, val_loader, epochs=50)

# Save model
trainer.save_model("cough_classifier.pt")
```

### Making Predictions

```python
from main import CoughClassifierTrainer, CoughClassifier
import torch

# Load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CoughClassifier(num_classes=6)
trainer = CoughClassifierTrainer(model, device=device)
trainer.load_model("cough_classifier.pt")

# Make prediction
disease, confidence, all_probabilities = trainer.predict("path/to/audio.wav")

print(f"Predicted Disease: {disease}")
print(f"Confidence: {confidence:.2%}")
print(f"All Probabilities: {all_probabilities}")
```

## Training Parameters

- **Batch Size**: 16
- **Learning Rate**: 0.001 (with ReduceLROnPlateau scheduler)
- **Optimizer**: Adam
- **Loss Function**: CrossEntropyLoss
- **Epochs**: 50 (with early stopping at patience=10)
- **Dropout**: 0.5 (first FC layer), 0.3 (second FC layer)

## Audio Processing

- **Sample Rate**: 16,000 Hz
- **Duration**: 3 seconds (normalized)
- **Mel-Spectrogram**:
  - Bins: 64
  - FFT Size: 400
  - Hop Length: 160
- **Normalization**: Z-score normalization applied to each spectrogram

## Model Performance Considerations

- **Minimum Training Samples**: 20-30 samples per class recommended
- **Optimal Training Samples**: 100+ samples per class
- **GPU Memory**: ~2GB sufficient for batch size 16
- **Training Time**: ~5-10 minutes per epoch (varies by dataset size)

## Troubleshooting

1. **Out of Memory**: Reduce batch size to 8 or lower
2. **Audio Loading Errors**: Ensure audio files are valid WAV or MP3 format
3. **Poor Performance**: Ensure balanced dataset across classes
4. **Slow Training**: GPU may not be available; install CUDA/cuDNN

## Future Improvements

- Mixup data augmentation
- Ensemble methods
- Transfer learning with pretrained models
- Time-frequency augmentation
- Class weighting for imbalanced datasets
- Cross-validation for robust evaluation

## License

This project is part of the UN Hackathon initiative.

## References

- PyTorch Documentation: https://pytorch.org/
- Torchaudio: https://pytorch.org/audio/
- Mel-Spectrogram Processing: https://en.wikipedia.org/wiki/Mel-scale
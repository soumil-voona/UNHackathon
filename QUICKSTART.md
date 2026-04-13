# Quick Start Guide

## Installation

### 1. Clone/Setup the Project
```bash
cd UNHackathon
```

### 2. Create a Python Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Data Preparation

### Organize Your Audio Files
Create an `audio_data` directory with the following structure:

```
audio_data/
├── Healthy/
│   ├── healthy_001.wav
│   ├── healthy_002.wav
│   └── ...
├── Cold Cough/
│   ├── cold_001.wav
│   ├── cold_002.wav
│   └── ...
├── COVID-19/
│   ├── covid_001.wav
│   └── ...
├── Asthma/
│   └── ...
├── Bronchitis/
│   └── ...
└── Whooping Cough/
    └── ...
```

**Supported formats:** `.wav`, `.mp3`, `.m4a`, `.flac`

**Recommended minimum:** 20-30 samples per class for basic training, 100+ for production.

## Usage

### Option 1: Training from Command Line

```bash
# Basic training (uses default audio_data directory)
python train.py

# Custom parameters
python train.py --audio-dir your_data/ --batch-size 32 --epochs 100 --learning-rate 0.0001 --output my_model.pt
```

### Option 2: Training with Python Script

```python
from main import CoughClassifier, CoughClassifierTrainer, CoughAudioDataset
from torch.utils.data import DataLoader, random_split
import torch

# Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CoughClassifier(num_classes=6)
trainer = CoughClassifierTrainer(model, device=device)

# Load data
dataset = CoughAudioDataset("audio_data")
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

# Train
trainer.train(train_loader, val_loader, epochs=50)
trainer.save_model("my_model.pt")
```

### Option 3: Making Predictions

**Simple Inference:**
```python
from inference import CoughInference

# Initialize
inference = CoughInference(model_path="cough_classifier.pt")

# Classify single file
result = inference.classify_audio("path/to/audio.wav")
print(result)
# Output: {
#   "audio_file": "path/to/audio.wav",
#   "predicted_disease": "COVID-19",
#   "confidence": 0.92,
#   "all_probabilities": {
#       "Healthy": 0.01,
#       "Cold Cough": 0.03,
#       "COVID-19": 0.92,
#       ...
#   }
# }
```

**Batch Processing:**
```python
# Classify all files in a directory
results = inference.classify_multiple("test_audio_directory/")
inference.save_results(results, "predictions.json")
```

### Option 4: REST API

**Start the API Server:**
```bash
python api.py
```

Server runs on `http://localhost:5000`

**API Endpoints:**

1. **Health Check**
```bash
curl http://localhost:5000/health
```

2. **Get Available Classes**
```bash
curl http://localhost:5000/classes
```

3. **Predict from File Upload**
```bash
curl -X POST -F "audio=@your_audio.wav" http://localhost:5000/predict
```

4. **Get Top-K Predictions**
```bash
curl -X POST -F "audio=@your_audio.wav" -F "top_k=3" http://localhost:5000/top-predictions
```

### Option 5: View Examples

```bash
python examples.py
```

Follow the interactive menu to see different usage patterns.

## Model Details

### Architecture
- **Input:** Mel-spectrogram (64 bins, 3-second duration)
- **Backbone:** 4 convolutional layers (32→64→128→256 filters)
- **Features:** Batch normalization, dropout, adaptive pooling
- **Output:** 6-class probability distribution

### Training Configuration
- **Optimizer:** Adam
- **Loss:** Cross-Entropy Loss
- **Scheduler:** ReduceLROnPlateau
- **Early Stopping:** Patience=10 epochs
- **Batch Size:** 16 (adjustable)
- **Default Learning Rate:** 0.001

### Audio Processing
- **Sample Rate:** 16,000 Hz
- **Duration:** 3 seconds (auto-padded/trimmed)
- **Features:** Mel-spectrogram with 64 bins
- **Normalization:** Z-score (per-sample)

## Performance Optimization

### Reducing Memory Usage
```python
# Reduce batch size during training
trainer = CoughClassifierTrainer(model, device=device)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
```

### Using GPU
```python
# Automatically uses GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CoughClassifier(num_classes=6)
trainer = CoughClassifierTrainer(model, device=device)
```

### Transfer Learning
```python
# Load pre-trained model
model.load_state_dict(torch.load("cough_classifier.pt"))

# Freeze early layers
for param in model.conv1.parameters():
    param.requires_grad = False

# Fine-tune with lower learning rate
trainer = CoughClassifierTrainer(model, learning_rate=0.0001)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No audio files found` | Check directory structure matches expected format |
| `Out of Memory` | Reduce batch size in training |
| `GPU not detected` | Verify CUDA/cuDNN installation for GPU support |
| `Poor accuracy` | Increase training data, adjust hyperparameters |
| `Audio loading errors` | Verify audio file format (WAV/MP3) and integrity |

## File Guide

| File | Purpose |
|------|---------|
| `main.py` | Core model, dataset, and trainer classes |
| `train.py` | Command-line training script |
| `inference.py` | Inference utilities for predictions |
| `api.py` | Flask REST API server |
| `examples.py` | Usage examples |
| `requirements.txt` | Python dependencies |

## Next Steps

1. **Collect Data:** Gather cough audio samples for your target classes
2. **Prepare Data:** Organize audio files in the required directory structure
3. **Train Model:** Run training script with your data
4. **Evaluate:** Monitor validation accuracy and loss
5. **Deploy:** Use inference script or API for predictions

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review examples.py for code samples
3. Check error messages for specific guidance
4. Verify data format and directory structure

## Notes

- Minimum recommended training time: 5-10 minutes per epoch
- Model expects mono audio, stereo will be converted
- Audio will be resampled to 16,000 Hz if needed
- Data augmentation (future enhancement)
- Cross-validation support (future enhancement)

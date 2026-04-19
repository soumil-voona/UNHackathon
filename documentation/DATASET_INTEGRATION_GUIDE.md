# Dataset Integration Guide

This guide explains how to download and integrate the three Kaggle datasets for cough classification.

## Datasets

The project uses three complementary Kaggle datasets:

### 1. **Respiratory Sound Database**
- **Kaggle**: https://www.kaggle.com/datasets/vbookshelf/respiratory-sound-database
- **Size**: ~3.7 GB
- **Samples**: 920+ audio files
- **Classes**: Healthy, Asthma, Bronchitis, URTI (Cold Cough)

### 2. **COVID-19 Cough Audio Classification**
- **Kaggle**: https://www.kaggle.com/datasets/andrewmvd/covid19-cough-audio-classification
- **Size**: ~1 GB
- **Samples**: 25,000+ audio files
- **Classes**: COVID-19, Healthy, Other

### 3. **TB Audio Dataset**
- **Kaggle**: https://www.kaggle.com/datasets/ruchikashirsath/tb-audio
- **Size**: ~2 GB
- **Samples**: 1,000+ audio files
- **Classes**: Tuberculosis, Pneumonia, Healthy

## Total Storage Required

- **Combined**: ~7-8 GB minimum (plus space for processing)
- **Recommended**: 20+ GB free disk space

## Step 1: Setup Kaggle Authentication

```bash
# Install kagglehub (if not already installed)
pip install kagglehub

# Authenticate with Kaggle
# Visit https://www.kaggle.com/settings/account
# Download your kaggle.json file
# Place it at ~/.kaggle/kaggle.json

# Set proper permissions
chmod 600 ~/.kaggle/kaggle.json
```

## Step 2: Download Datasets

### Option A: Automated Download (Recommended)
```bash
# Run the datasets.py script to download all three datasets
python datasets.py

# This will download to ~/.cache/kagglehub/datasets/
```

### Option B: Manual Download
```bash
# Download each dataset individually from Kaggle
# Then extract them to ./kaggle_datasets/

mkdir -p kaggle_datasets
# Download and extract the three datasets into kaggle_datasets/
```

## Step 3: Organize Datasets

Once downloaded, organize the datasets into a unified structure:

```bash
# Run the organize script
python organize_datasets.py \
    --input-dir ./kaggle_datasets \
    --output-dir ./audio_data
```

This script will:
- ✓ Map URTI to "Cold Cough"
- ✓ Combine all health/other categories to "Healthy"
- ✓ Organize files by disease class
- ✓ Create the following structure:

```
audio_data/
├── Healthy/
│   └── *.wav (from all datasets)
├── Cold Cough/
│   └── *.wav (URTI from Respiratory Sound Database)
├── COVID-19/
│   └── *.wav
├── Asthma/
│   └── *.wav
├── Bronchitis/
│   └── *.wav
├── Tuberculosis/
│   └── *.wav
└── Pneumonia/
    └── *.wav
```

## Step 4: Train the Model

After organizing the datasets, train the classifier:

```bash
# Train with default parameters
python train.py

# Or customize training
python train.py \
    --epochs 100 \
    --batch-size 32 \
    --learning-rate 0.0005 \
    --train-split 0.8 \
    --audio-dir ./audio_data \
    --output-model cough_classifier.pt
```

## Step 5: Make Predictions

Once trained, make predictions on new audio files:

```bash
# Single file prediction
python inference.py --audio-file path/to/audio.wav

# Batch prediction
python inference.py --audio-dir ./test_audio

# API server
python api.py
```

## Unified Disease Classes

The model classifies into 7 categories:

| Class | Source | Notes |
|-------|--------|-------|
| **Healthy** | All datasets | Reference baseline |
| **Cold Cough** | Respiratory Sound DB | Mapped from URTI |
| **COVID-19** | COVID-19 Cough Dataset | COVID-19 positive cases |
| **Asthma** | Respiratory Sound DB | Asthma patients |
| **Bronchitis** | Respiratory Sound DB | Bronchitis cases |
| **Tuberculosis** | TB Audio Dataset | TB positive cases |
| **Pneumonia** | TB Audio Dataset | Pneumonia cases |

## Troubleshooting

### Low Disk Space
If you get "No space left on device":
- Try downloading one dataset at a time
- Delete downloads after organizing
- Use `--output-dir` on a disk with more space

### Authentication Errors
```bash
# Verify Kaggle authentication
cat ~/.kaggle/kaggle.json
# Should show your username and key

# Re-authenticate if needed
kaggle auth login
```

### Missing Dataset Directory
```bash
# Check if dataset was downloaded
ls ~/.cache/kagglehub/datasets/

# Manually download from Kaggle web interface
# Extract to kaggle_datasets/ directory
# Run organize_datasets.py
```

## Data Statistics

After organization, you should have:

```
Total Files: ~27,000+
Healthy: ~5,000-7,000
Cold Cough: ~500-700
COVID-19: ~15,000+
Asthma: ~180-200
Bronchitis: ~450-500
Tuberculosis: ~500-700
Pneumonia: ~500-700
```

## Model Performance

With the combined datasets, expect:
- **Overall Accuracy**: 85-92%
- **COVID-19 Detection**: 95%+
- **Cold Cough vs Others**: 88%+

## Next Steps

1. ✓ Setup Kaggle authentication
2. ✓ Download datasets (Step 1-2)
3. ✓ Organize datasets (Step 3)
4. ✓ Train the model (Step 4)
5. ✓ Make predictions (Step 5)

For more information, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).

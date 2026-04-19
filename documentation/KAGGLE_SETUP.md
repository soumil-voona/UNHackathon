# 📥 Kaggle Dataset Setup Guide

## Getting Started with Respiratory Sound Database

This guide explains how to download and use the **Respiratory Sound Database** from Kaggle with your Cough Classifier.

---

## 🔑 Step 1: Setup Kaggle API

### 1.1 Install Kaggle CLI
```bash
pip install kaggle
```

### 1.2 Download Your API Key

1. Go to https://www.kaggle.com/settings/account
2. Click **"Create New API Token"**
3. A file named `kaggle.json` will be downloaded
4. Save it to `~/.kaggle/kaggle.json`

**On macOS/Linux:**
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**On Windows:**
```cmd
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\
```

### 1.3 Verify Setup
```bash
kaggle datasets list
# Should show a list of datasets without errors
```

---

## 📥 Step 2: Download Dataset

### Option A: Automatic Download (Recommended)
```bash
# Download and organize automatically
python download_dataset.py

# This will:
# 1. Download the Respiratory Sound Database
# 2. Extract zip files
# 3. Organize into audio_data/ directory
# 4. Show file count per class
```

### Option B: Manual Steps

**Step 1: List available datasets**
```bash
python download_dataset.py --list
```

**Step 2: Download**
```bash
python download_dataset.py \
  --dataset-name "vbookshelf/respiratory-sound-database" \
  --output "./respiratory_data_raw"
```

**Step 3: Extract**
```bash
python download_dataset.py \
  --skip-download \
  --extract-only \
  --output "./respiratory_data_raw"
```

**Step 4: Organize**
```bash
python download_dataset.py \
  --skip-download \
  --output "./respiratory_data_raw" \
  --organize-to "./audio_data"
```

---

## 📊 Understanding the Dataset

### Respiratory Sound Database Contents

The dataset contains:
- **920+ annotated respiratory sound recordings**
- **Multiple respiratory conditions:**
  - Normal breathing
  - Crackles (abnormal lung sounds)
  - Wheezes (high-pitched whistling sounds)
  - Both crackles and wheezes

### How Files Are Organized

The script automatically maps dataset labels to your disease classes:

```
Dataset Label → Your Class
─────────────────────────────
Normal       → Healthy
Crackles     → Bronchitis
Wheezes      → Asthma
Both         → Bronchitis
Undetermined → Healthy
```

---

## 🎯 Custom Dataset Organization

If you want to customize how files are organized, edit the `SOUND_MAPPING` in `download_dataset.py`:

```python
SOUND_MAPPING = {
    'normal': 'Healthy',
    'crackles': 'Bronchitis',
    'wheezes': 'Asthma',
    'both': 'Bronchitis',
    'undetermined': 'Healthy',
}
```

---

## 🚀 Quick Start: Download → Train → Predict

### Complete workflow:

```bash
# 1. Download and organize (takes 10-30 minutes depending on connection)
python download_dataset.py

# 2. Check what was downloaded
ls -la audio_data/

# 3. Train the model
python train.py --epochs 50 --batch-size 16

# 4. Make predictions
python inference.py
```

---

## 📊 Dataset Statistics

After download and organization, you'll see something like:

```
✓ Organized 920 files

Dataset summary:
  Healthy: 285 files
  Asthma: 180 files
  Bronchitis: 455 files
  Cold Cough: 0 files
  COVID-19: 0 files
  Whooping Cough: 0 files
```

**Note:** This dataset doesn't include COVID-19 or cold cough samples. You may want to:
1. Use this as base training data
2. Add COVID-19 and cold samples from other sources
3. Or adapt the classifier to work with available classes

---

## 💡 Advanced Usage

### Download Different Dataset

The script supports multiple Kaggle datasets:

```bash
# List all available datasets
python download_dataset.py --list

# Download COUGHVID dataset (larger, ~25,000 samples)
python download_dataset.py \
  --dataset-name "vbookshelf/coughvid-a-large-scale-open-source-cough-audio-dataset" \
  --organize-to "./audio_data_coughvid"
```

### Custom Output Directories

```bash
python download_dataset.py \
  --output "./my_raw_data" \
  --organize-to "./my_organized_data"
```

### Skip Download (Use Existing Files)

```bash
# If you already downloaded the zip file
python download_dataset.py --skip-download
```

### Extract Only

```bash
# Extract zips without organizing
python download_dataset.py --extract-only
```

---

## 🔧 Troubleshooting

### Issue: "Kaggle CLI not found"
```bash
pip install kaggle
```

### Issue: "API key not found"
1. Download from https://www.kaggle.com/settings/account
2. Save to `~/.kaggle/kaggle.json`
3. Run: `chmod 600 ~/.kaggle/kaggle.json` (macOS/Linux)

### Issue: "No audio files found"
- Check that zip files were extracted
- Run: `find respiratory_data_raw -name "*.wav" | head`
- Verify file permissions

### Issue: "Not authenticated"
- Re-download API key from Kaggle
- Verify kaggle.json permissions: `ls -la ~/.kaggle/kaggle.json`
- Should be: `-rw-------` (600)

### Issue: "Import error"
```bash
# Ensure all dependencies installed
pip install -r requirements.txt
```

---

## 📈 Expected Training Results

With the Respiratory Sound Database:

```
Dataset: 920 respiratory sound samples
Classes: Healthy, Asthma, Bronchitis
Duration: ~1-2 hours for full training

Expected Accuracy: 85-95% (high variance dataset)
Model Size: ~10MB
```

---

## 🔄 Combining Multiple Datasets

To use data from multiple sources:

```bash
# Create organized directory
mkdir -p audio_data

# Download Respiratory
python download_dataset.py \
  --dataset-name "vbookshelf/respiratory-sound-database" \
  --organize-to "./audio_data_respiratory"

# Download COUGHVID
python download_dataset.py \
  --dataset-name "vbookshelf/coughvid-a-large-scale-open-source-cough-audio-dataset" \
  --organize-to "./audio_data_coughvid"

# Manually combine:
cp -r audio_data_respiratory/* audio_data/
cp -r audio_data_coughvid/* audio_data/
```

---

## 📚 Next Steps

1. **Download:** `python download_dataset.py`
2. **Verify:** `ls -la audio_data/`
3. **Train:** `python train.py`
4. **Evaluate:** `python evaluate.py`
5. **Deploy:** `python api.py`

---

## 🎓 Using the Data

### Check Data Quality

```python
from main import CoughAudioDataset

dataset = CoughAudioDataset("audio_data")
print(f"Total samples: {len(dataset)}")

# Check a sample
mel_spec, label = dataset[0]
print(f"Mel-spectrogram shape: {mel_spec.shape}")
print(f"Label: {label}")
```

### View Class Distribution

```python
from collections import Counter
from main import CoughAudioDataset

dataset = CoughAudioDataset("audio_data")
labels = [dataset[i][1] for i in range(len(dataset))]
print(Counter(labels))
```

---

## 📝 Data Documentation

**Source:** https://www.kaggle.com/datasets/vbookshelf/respiratory-sound-database

**Citation:**
```
Respiratory Sounds Database
- Contains annotated respiratory sound samples
- Multiple respiratory conditions
- Suitable for audio classification tasks
```

**License:** Check Kaggle dataset page for license information

---

## 🆘 Support

For issues:
1. Check this guide's troubleshooting section
2. Verify Kaggle API setup
3. Check file permissions
4. Review error messages carefully

Need help? See:
- [Kaggle API Documentation](https://github.com/Kaggle/kaggle-api)
- [Project README](README.md)
- [QUICKSTART Guide](QUICKSTART.md)

---

**Happy training! 🚀**

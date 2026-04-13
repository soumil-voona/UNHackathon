# 🎓 Complete Guide: Using Kaggle Respiratory Sound Database

## Overview

You now have a complete workflow to download the **Respiratory Sound Database** from Kaggle and use it to train your cough classifier model.

---

## 📋 What You Have

### New Files Created

1. **download_dataset.py** - Main dataset downloader
   - Downloads from Kaggle
   - Extracts zip files
   - Organizes into disease classes
   - Automatic label mapping

2. **manage_datasets.py** - Advanced dataset manager
   - Download multiple datasets
   - Combine multiple sources
   - Get dataset statistics
   - Batch operations

3. **KAGGLE_SETUP.md** - Detailed setup guide
   - Step-by-step instructions
   - Troubleshooting
   - Advanced usage
   - Multiple dataset examples

4. **KAGGLE_QUICK_REFERENCE.md** - Quick commands
   - One-command setup
   - Common tasks
   - Quick verification

5. **requirements.txt** - Updated with `kaggle` package

---

## 🚀 Quick Start (3 Steps)

### Step 1: Setup Kaggle API

```bash
# Install Kaggle
pip install kaggle

# Download API key from: https://www.kaggle.com/settings/account

# Save to: ~/.kaggle/kaggle.json

# Set permissions (macOS/Linux)
chmod 600 ~/.kaggle/kaggle.json
```

### Step 2: Download Dataset

```bash
# Download and organize automatically
python download_dataset.py

# This takes 10-30 minutes depending on your internet speed
# Downloads ~2.5GB and organizes into audio_data/
```

### Step 3: Train Model

```bash
# Train with downloaded data
python train.py --epochs 50
```

---

## 📊 Kaggle Dataset Information

### Respiratory Sound Database
- **Source:** https://www.kaggle.com/datasets/vbookshelf/respiratory-sound-database
- **Size:** ~2.5 GB
- **Samples:** 920+ annotated respiratory sound recordings
- **Classes:** Normal, Crackles, Wheezes, Both

### Class Mapping

The downloader automatically maps the dataset labels to your disease classes:

```
Respiratory Dataset    →    Your Classes
────────────────────────────────────────
Normal                 →    Healthy
Crackles               →    Bronchitis
Wheezes                →    Asthma
Both Crackles/Wheezes  →    Bronchitis
Undetermined           →    Healthy
```

---

## 🛠️ Available Commands

### Basic Download
```bash
python download_dataset.py
```
Downloads, extracts, and organizes automatically.

### List Available Datasets
```bash
python download_dataset.py --list
```
Shows all available Kaggle datasets you can download.

### Custom Output Directories
```bash
python download_dataset.py \
  --output "./my_raw_data" \
  --organize-to "./my_audio_data"
```

### Skip Download (Use Existing Files)
```bash
python download_dataset.py --skip-download
```
Useful if you already have the zip files.

### Extract Only
```bash
python download_dataset.py --extract-only
```
Just extract without organizing.

### Advanced: Combine Multiple Datasets
```bash
# List available datasets
python manage_datasets.py --list-datasets

# Combine specific datasets
python manage_datasets.py --combine respiratory coughvid

# Download and combine in one step
python manage_datasets.py --download-combine respiratory coughvid

# Get statistics
python manage_datasets.py --stats audio_data
```

---

## 📁 Directory Structure After Download

```
Your Project/
├── download_dataset.py          # Downloader script
├── manage_datasets.py           # Dataset manager
├── train.py                     # Training script
├── inference.py                 # Inference
├── audio_data/                  # Organized data
│   ├── Healthy/                 # 285 files
│   ├── Asthma/                  # 180 files
│   ├── Bronchitis/              # 455 files
│   ├── Cold Cough/              # 0 files (not in this dataset)
│   ├── COVID-19/                # 0 files (not in this dataset)
│   └── Whooping Cough/          # 0 files (not in this dataset)
└── respiratory_data_raw/        # Raw downloaded files
    ├── *.zip
    └── extracted files
```

---

## ✅ Verification Steps

### 1. Check Kaggle Setup
```bash
kaggle datasets list | head
```
Should show list of datasets without errors.

### 2. Check Downloaded Files
```bash
ls -lh respiratory_data_raw/ | head
du -sh respiratory_data_raw/
```

### 3. Check Organized Data
```bash
ls -la audio_data/
du -sh audio_data/*/
find audio_data -name "*.wav" | wc -l
```

### 4. Check Specific Class
```bash
ls -la audio_data/Healthy/ | head
ls audio_data/Asthma | wc -l
```

---

## 🎯 Training with Downloaded Data

### Quick Training
```bash
python train.py
```
Uses default audio_data/ directory.

### Custom Parameters
```bash
python train.py \
  --epochs 50 \
  --batch-size 16 \
  --learning-rate 0.001 \
  --train-split 0.8
```

### Monitor Training
The trainer will display:
```
Epoch 1/50
  Train Loss: 1.2345, Train Acc: 65.23%
  Val Loss: 1.1234, Val Acc: 70.45%
...
```

### After Training
Model is saved as `cough_classifier.pt` (or custom name with `--output`)

---

## 🔍 Troubleshooting

### Problem: "Kaggle CLI not found"
**Solution:**
```bash
pip install kaggle
```

### Problem: "API key not found"
**Solution:**
1. Go to https://www.kaggle.com/settings/account
2. Click "Create New API Token"
3. Save `kaggle.json` to `~/.kaggle/`
4. Run: `chmod 600 ~/.kaggle/kaggle.json`

### Problem: "Not authenticated"
**Solution:**
```bash
# Verify API key location
ls -la ~/.kaggle/kaggle.json

# Check permissions (should be -rw-------)
# Fix permissions if needed
chmod 600 ~/.kaggle/kaggle.json
```

### Problem: "No audio files found"
**Solution:**
1. Check if download completed: `ls respiratory_data_raw/`
2. Check if files exist: `find respiratory_data_raw -name "*.wav" | wc -l`
3. Try extract only: `python download_dataset.py --extract-only`

### Problem: Slow Download
**Solution:**
- Normal speed: 1-3 MB/sec
- Expected time: 15-40 minutes
- Check internet connection
- Can pause/resume

### Problem: Disk Space
**Solution:**
- Dataset size: ~2.5 GB (compressed), ~3-4 GB (extracted)
- Ensure you have 5+ GB free space
- Can delete raw files after organizing: `rm -rf respiratory_data_raw/`

---

## 💡 Tips & Tricks

### 1. Keep Raw Files (for reproducibility)
```bash
# Don't delete respiratory_data_raw/
# Useful if you need to re-organize differently
```

### 2. Multiple Organized Versions
```bash
# Create different organized versions
python download_dataset.py --organize-to "./audio_data_v1"
# Edit SOUND_MAPPING in download_dataset.py
python download_dataset.py --skip-download --organize-to "./audio_data_v2"

# Train with different versions
python train.py --audio-dir ./audio_data_v1
python train.py --audio-dir ./audio_data_v2
```

### 3. Combine with Other Data
```bash
# After organizing this dataset
python download_dataset.py

# Manually add files from other sources
cp /path/to/covid_samples/* audio_data/COVID-19/
cp /path/to/cold_samples/* audio_data/"Cold Cough"/

# Re-train
python train.py
```

### 4. Check Data Quality
```python
from main import CoughAudioDataset
import matplotlib.pyplot as plt

dataset = CoughAudioDataset("audio_data")

# Check a sample
mel_spec, label = dataset[0]
plt.imshow(mel_spec[0])
plt.show()

# Check dataset info
print(f"Total samples: {len(dataset)}")
```

### 5. Data Augmentation
```bash
# After organizing, can apply augmentation
# See evaluate.py for visualization of data
python evaluate.py --show-samples
```

---

## 📊 Expected Dataset After Download

```
Total files: 920

Class Distribution:
  Healthy: 285 files (31%)
  Asthma: 180 files (20%)
  Bronchitis: 455 files (49%)
  Other classes: 0 files
```

**Note:** This dataset focuses on respiratory sounds, not COVID-19 or cold coughs. You may want to:
1. Use only these classes for training
2. Find additional COVID-19/cold data from other sources
3. Adapt the model to use available classes

---

## 🔗 Additional Resources

### Kaggle Datasets
- **Respiratory**: https://www.kaggle.com/datasets/vbookshelf/respiratory-sound-database
- **COUGHVID**: https://www.kaggle.com/datasets/vbookshelf/coughvid-a-large-scale-open-source-cough-audio-dataset
- **More**: Search "cough" on Kaggle.com

### Documentation
- **KAGGLE_SETUP.md** - Detailed setup guide
- **KAGGLE_QUICK_REFERENCE.md** - Quick commands
- **README.md** - Full project documentation
- **QUICKSTART.md** - Quick start guide

### Tools
- **download_dataset.py** - Main downloader
- **manage_datasets.py** - Advanced dataset management
- **train.py** - Training script
- **inference.py** - Inference utilities

---

## 🎓 Complete Workflow

```bash
# 1. Install packages
pip install -r requirements.txt

# 2. Setup Kaggle API (one time)
# Download from https://www.kaggle.com/settings/account
# Save to ~/.kaggle/kaggle.json
# chmod 600 ~/.kaggle/kaggle.json

# 3. Download and organize data
python download_dataset.py

# 4. Verify data
ls -la audio_data/
find audio_data -name "*.wav" | wc -l

# 5. Train model
python train.py --epochs 50

# 6. Make predictions
python inference.py

# 7. Evaluate
python evaluate.py

# 8. Deploy
python api.py
```

---

## ✨ What's Next?

1. **Setup Kaggle API** - 5 minutes
2. **Download Dataset** - 20-40 minutes
3. **Train Model** - 1-2 hours
4. **Evaluate Results** - 10 minutes
5. **Deploy API** - 5 minutes

**Total Time:** ~2-3 hours for complete setup and training

---

## 🎉 You're All Set!

You now have:
- ✅ Complete download workflow
- ✅ Automatic data organization
- ✅ Dataset management tools
- ✅ Training pipeline
- ✅ Inference utilities
- ✅ Comprehensive documentation

**Next Step:** Run `python download_dataset.py` to get started!

---

**Need Help?** See:
- KAGGLE_SETUP.md - Detailed guide
- KAGGLE_QUICK_REFERENCE.md - Quick commands
- README.md - Project documentation

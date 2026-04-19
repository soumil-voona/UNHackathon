# ⚡ Quick Reference: Kaggle Dataset Download

## One Command Setup

```bash
# Install dependencies
pip install kaggle

# Setup Kaggle API (one time only)
# 1. Download from: https://www.kaggle.com/settings/account
# 2. Place at: ~/.kaggle/kaggle.json
# 3. Run: chmod 600 ~/.kaggle/kaggle.json

# Download and organize dataset
python download_dataset.py

# Train model
python train.py

# Make predictions
python inference.py
```

---

## 🎯 Available Commands

### List Datasets
```bash
python download_dataset.py --list
```

### Download & Organize (Default)
```bash
python download_dataset.py
```

### Custom Output Directory
```bash
python download_dataset.py \
  --dataset-name "vbookshelf/respiratory-sound-database" \
  --output "./my_data" \
  --organize-to "./my_audio_data"
```

### Skip Download (Use Existing)
```bash
python download_dataset.py --skip-download
```

### Extract Only
```bash
python download_dataset.py --extract-only
```

---

## 🔗 Dataset Links

| Dataset | Size | Samples | Command |
|---------|------|---------|---------|
| Respiratory | ~2.5 GB | 920+ | `python download_dataset.py` |
| COUGHVID | ~7 GB | 25,000+ | `--dataset-name coughvid` |
| Urban Sound | ~6 GB | 8,732 | `--dataset-name urban-sound` |

---

## 📋 Verification

```bash
# Check downloaded files
ls -lh respiratory_data_raw/

# Check organized data
ls -la audio_data/
du -sh audio_data/*/

# Check specific class
ls audio_data/Healthy | wc -l
```

---

## ✅ Success Indicators

After running `python download_dataset.py`, you should see:

```
✓ Organized 920 files

Dataset summary:
  Healthy: 285 files
  Asthma: 180 files
  Bronchitis: 455 files
  ...

✓ Data ready at: ./audio_data
```

---

## 🚀 Next: Training

```bash
python train.py --epochs 50 --batch-size 16
```

---

See **[KAGGLE_SETUP.md](KAGGLE_SETUP.md)** for detailed instructions.

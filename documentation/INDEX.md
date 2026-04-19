# 📚 Project Documentation Index

Welcome to the Cough Classifier project! This guide will help you navigate all available documentation and resources.

## 🎯 Where to Start?

### First Time Setup?
→ **[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** - Complete installation and setup guide

### Want Quick Start?
→ **[QUICKSTART.md](QUICKSTART.md)** - Fast setup and basic usage (5 minutes)

### Need Comprehensive Guide?
→ **[README.md](README.md)** - Full documentation with all details

### Want Project Overview?
→ **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level project summary

---

## 📋 File Guide

### Core Implementation

| File | Purpose | Lines |
|------|---------|-------|
| **[main.py](main.py)** | Main model implementation | ~500 |
| Contains: CoughClassifier, CoughAudioDataset, CoughClassifierTrainer | | |

### Scripts & Tools

| File | Purpose | Usage |
|------|---------|-------|
| **[train.py](train.py)** | CLI training script | `python train.py --help` |
| **[inference.py](inference.py)** | Inference utilities | For batch prediction |
| **[api.py](api.py)** | Flask REST API | `python api.py` |
| **[evaluate.py](evaluate.py)** | Model evaluation | Metrics & visualizations |
| **[examples.py](examples.py)** | Usage examples | `python examples.py` |
| **[setup.py](setup.py)** | Automated setup | `python setup.py` |
| **[config.py](config.py)** | Configuration | Centralized settings |

### Documentation

| File | Purpose |
|------|---------|
| **[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** | Installation & setup (THIS FILE) |
| **[README.md](README.md)** | Comprehensive documentation |
| **[QUICKSTART.md](QUICKSTART.md)** | Quick start guide |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Project overview |
| **[INDEX.md](INDEX.md)** | Documentation index (THIS FILE) |

### Configuration

| File | Purpose |
|------|---------|
| **[requirements.txt](requirements.txt)** | Python dependencies |
| **[.gitignore](.gitignore)** | Git ignore patterns |

---

## 🚀 Quick Navigation

### Installation & Setup
1. [INSTALL_GUIDE.md](INSTALL_GUIDE.md) → Complete setup with dependencies
2. [QUICKSTART.md](QUICKSTART.md) → 5-minute quick start

### Using the Model
- Training → See [QUICKSTART.md](QUICKSTART.md) or `python train.py --help`
- Single Prediction → [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md)
- Batch Processing → [inference.py](inference.py)
- REST API → `python api.py` then see [README.md](README.md)

### Advanced Usage
- Model Architecture → [README.md](README.md) → Model Architecture section
- Training Parameters → [config.py](config.py)
- Evaluation → [evaluate.py](evaluate.py)
- Transfer Learning → [examples.py](examples.py) → Example 5
- Custom Training → [main.py](main.py) → CoughClassifierTrainer class

### Troubleshooting
- Common Issues → [QUICKSTART.md](QUICKSTART.md) → Troubleshooting section
- Installation Issues → [INSTALL_GUIDE.md](INSTALL_GUIDE.md)
- Training Issues → [README.md](README.md) → Training Parameters
- API Issues → [api.py](api.py) → Comments

---

## 📊 Feature Matrix

| Feature | File | Status |
|---------|------|--------|
| Model Architecture | main.py | ✅ Complete |
| Training Pipeline | train.py | ✅ Complete |
| Single Inference | inference.py | ✅ Complete |
| Batch Processing | inference.py | ✅ Complete |
| REST API | api.py | ✅ Complete |
| Evaluation Tools | evaluate.py | ✅ Complete |
| Configuration | config.py | ✅ Complete |
| Documentation | README.md | ✅ Complete |
| Examples | examples.py | ✅ Complete |
| Setup Script | setup.py | ✅ Complete |

---

## 🎓 Learning Path

### Beginner
1. Read [INSTALL_GUIDE.md](INSTALL_GUIDE.md)
2. Run `python setup.py`
3. Follow [QUICKSTART.md](QUICKSTART.md)
4. Train first model: `python train.py`
5. Make prediction: See [QUICKSTART.md](QUICKSTART.md)

### Intermediate
1. Understand architecture: [README.md](README.md) → Model Architecture
2. Customize config: Edit [config.py](config.py)
3. Run examples: `python examples.py`
4. Batch processing: Use [inference.py](inference.py)
5. REST API: `python api.py`

### Advanced
1. Study model code: [main.py](main.py)
2. Implement custom loss: Edit [main.py](main.py)
3. Transfer learning: [examples.py](examples.py) → Example 5
4. Model evaluation: [evaluate.py](evaluate.py)
5. Deployment: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) → Deployment

---

## 💡 Common Tasks

### "I want to train a model"
→ [QUICKSTART.md](QUICKSTART.md) → Usage → Training

### "I want to make predictions"
→ [QUICKSTART.md](QUICKSTART.md) → Usage → Making Predictions

### "I want to deploy an API"
→ [README.md](README.md) → REST API Endpoints

### "I want to evaluate my model"
→ [evaluate.py](evaluate.py) → `evaluate_on_test_directory()`

### "I want to understand the model"
→ [README.md](README.md) → Model Architecture

### "I want to customize hyperparameters"
→ [config.py](config.py) → Edit settings

### "I want to see code examples"
→ [examples.py](examples.py) → Run examples

### "I'm having issues"
→ [QUICKSTART.md](QUICKSTART.md) → Troubleshooting

---

## 🔧 Configuration Guide

All settings are in [config.py](config.py):

```python
# Audio Settings
SAMPLE_RATE = 16000
N_MELS = 64

# Model Settings
NUM_CLASSES = 6
INITIAL_FILTERS = 32

# Training Settings
BATCH_SIZE = 16
LEARNING_RATE = 0.001
NUM_EPOCHS = 50

# See config.py for all options
```

---

## 📱 API Quick Reference

### Health Check
```bash
curl http://localhost:5000/health
```

### Get Classes
```bash
curl http://localhost:5000/classes
```

### Predict
```bash
curl -X POST -F "audio=@audio.wav" http://localhost:5000/predict
```

→ Full API docs in [README.md](README.md) → REST API Endpoints

---

## 🎯 Project Structure

```
UNHackathon/
├── 📄 Documentation
│   ├── INDEX.md                  ← YOU ARE HERE
│   ├── INSTALL_GUIDE.md          ← Installation
│   ├── QUICKSTART.md             ← Quick start
│   ├── README.md                 ← Full docs
│   └── PROJECT_SUMMARY.md        ← Overview
│
├── 🔧 Core Implementation
│   └── main.py                   ← Model code
│
├── 🛠️ Tools & Scripts
│   ├── train.py                  ← Training
│   ├── inference.py              ← Predictions
│   ├── api.py                    ← REST API
│   ├── evaluate.py               ← Evaluation
│   ├── examples.py               ← Examples
│   ├── setup.py                  ← Setup
│   └── config.py                 ← Configuration
│
├── 📦 Configuration
│   ├── requirements.txt           ← Dependencies
│   └── .gitignore               ← Git config
│
└── 📁 Data (to be created)
    └── audio_data/
        ├── Healthy/
        ├── Cold Cough/
        ├── COVID-19/
        ├── Asthma/
        ├── Bronchitis/
        └── Whooping Cough/
```

---

## 🚀 Getting Started Now

### Option 1: Automated Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create data directories
mkdir -p audio_data/{Healthy,"Cold Cough","COVID-19",Asthma,Bronchitis,"Whooping Cough"}

# 3. Add your audio files to audio_data/

# 4. Train model
python train.py

# 5. Make predictions
python inference.py
```

---

## 📞 Support

| Issue | Resource |
|-------|----------|
| Installation | [INSTALL_GUIDE.md](INSTALL_GUIDE.md) |
| Quick start | [QUICKSTART.md](QUICKSTART.md) |
| Full details | [README.md](README.md) |
| Overview | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| Code examples | [examples.py](examples.py) |
| Configuration | [config.py](config.py) |
| Troubleshooting | [QUICKSTART.md](QUICKSTART.md) |

---

## 🎉 Ready?

1. **First time?** → Read [INSTALL_GUIDE.md](INSTALL_GUIDE.md)
2. **In a hurry?** → Follow [QUICKSTART.md](QUICKSTART.md)
3. **Need details?** → Check [README.md](README.md)
4. **Want overview?** → See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**Let's get started! 🚀**

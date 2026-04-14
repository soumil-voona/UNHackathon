#!/bin/bash
# Quick start script for dataset integration and model training

set -e

echo "🚀 Cough Classifier - Dataset Integration & Training"
echo "========================================================"

# Check Python
python_version=$(python --version 2>&1)
echo "✓ Python: $python_version"

# Check dependencies
echo ""
echo "📦 Checking dependencies..."
python -c "import torch; print('✓ PyTorch ' + torch.__version__)" 2>/dev/null || {
    echo "✗ PyTorch not installed. Run: pip install -r requirements.txt"
    exit 1
}

python -c "import kagglehub; print('✓ kagglehub installed')" 2>/dev/null || {
    echo "⚠ kagglehub not installed. Run: pip install kagglehub"
}

# Check Kaggle auth
echo ""
echo "🔐 Checking Kaggle authentication..."
if [ -f ~/.kaggle/kaggle.json ]; then
    echo "✓ Kaggle credentials found"
else
    echo "⚠ Kaggle credentials not found at ~/.kaggle/kaggle.json"
    echo "  Get yours from: https://www.kaggle.com/settings/account"
    echo "  Then: mkdir -p ~/.kaggle && cp kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json"
fi

# Disk space check
echo ""
echo "💾 Checking disk space..."
available_gb=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
echo "  Available: ${available_gb}GB"
if [ "$available_gb" -lt 20 ]; then
    echo "⚠ Warning: Less than 20GB available (needs ~7GB minimum)"
fi

# Show structure
echo ""
echo "📁 Directory structure:"
echo "  ✓ main.py              - CNN model implementation"
echo "  ✓ train.py            - Training script"
echo "  ✓ inference.py        - Prediction script"
echo "  ✓ organize_datasets.py - Dataset organization tool"
echo "  ✓ datasets.py         - Kaggle downloader"

# Show next steps
echo ""
echo "========================================================"
echo "📋 Next Steps:"
echo "========================================================"
echo ""
echo "1️⃣  Download datasets (requires ~7 GB):"
echo "    python datasets.py"
echo ""
echo "2️⃣  Organize downloaded datasets:"
echo "    python organize_datasets.py --input-dir ./kaggle_datasets --output-dir ./audio_data"
echo ""
echo "3️⃣  Train the model:"
echo "    python train.py --epochs 100 --batch-size 32"
echo ""
echo "4️⃣  Make predictions:"
echo "    python inference.py --audio-file path/to/audio.wav"
echo ""
echo "📖 For detailed instructions, see:"
echo "    - DATASET_INTEGRATION_GUIDE.md"
echo "    - DATASET_INTEGRATION_SUMMARY.md"
echo "    - README.md"
echo ""

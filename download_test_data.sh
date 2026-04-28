#!/bin/bash
# Script to download alternative test datasets from Kaggle
# These datasets were NOT used in training, perfect for testing

set -e

echo "Available test datasets from Kaggle:"
echo "======================================"
echo ""
echo "1. TB Audio Screening Dataset"
echo "   kaggle datasets download -d ruchikashirsath/tb-audio"
echo "   Contains: Tuberculosis, Pneumonia audio samples"
echo ""
echo "2. Pneumonia Detection from Cough Audio"
echo "   kaggle datasets download -d ayushtaggart/pneumonia-detection-cough-sounds"
echo "   Contains: Pneumonia-specific cough audio"
echo ""
echo "3. Sleep Apnea Audio Dataset"
echo "   kaggle datasets download -d fedesoriano/sleep-apnea"
echo "   Contains: Different respiratory condition audio"
echo ""
echo "======================================"
echo ""
echo "To download a dataset, run:"
echo "  kaggle datasets download -d <dataset_name>"
echo ""
echo "Then extract it:"
echo "  unzip <dataset_name>.zip -d test_data_new/"
echo ""
echo "Then test with:"
echo "  python test_model.py best_cough_classifier.pt ./test_data_new/"

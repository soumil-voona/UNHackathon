# Testing Your Trained Model on Unseen Data

This guide shows you how to use the trained cough classifier model to make predictions on new audio data.

## Quick Start

### Test a Single Audio File
```bash
python test_model.py best_cough_classifier.pt path/to/audio_file.wav
```

Output:
```
Testing single file: audio_file.wav
------------------------------------------------------------
File: path/to/audio_file.wav
Predicted Disease: Bronchitis
Confidence: 38.8%

All Class Probabilities:
  Bronchitis          : 0.3876
  Healthy             : 0.3402
  Asthma              : 0.2028
  Cold Cough          : 0.0327
  COVID-19            : 0.0135
  Tuberculosis        : 0.0127
  Pneumonia           : 0.0105
```

### Test All Files in a Directory
```bash
python test_model.py best_cough_classifier.pt ./audio_data/Healthy
```

Output:
```
Testing all audio files in: audio_data/Healthy
Found 920 audio files
✓ file_001.wav: Bronchitis (38.8%)
✓ file_002.wav: Healthy (45.2%)
...

===========================================================
CLASSIFICATION SUMMARY
===========================================================
Asthma              :    5 files (  0.5%)
Bronchitis          :  450 files ( 48.9%)
Cold Cough          :   10 files (  1.1%)
COVID-19            :    0 files (  0.0%)
Healthy             :  450 files ( 48.9%)
Pneumonia           :    5 files (  0.5%)
Tuberculosis        :    0 files (  0.0%)

Total files tested: 920
Results saved to: inference_results.json
```

## Command Line Options

### Basic Usage
```bash
python test_model.py <model_path> <data_path>
```

### Advanced Options
```bash
# Specify custom output file
python test_model.py best_cough_classifier.pt ./audio_data/Healthy --output my_results.json

# Force CPU device (useful if CUDA isn't available)
python test_model.py best_cough_classifier.pt ./audio_data/Healthy --device cpu

# Quiet mode (only show summary, not per-file output)
python test_model.py best_cough_classifier.pt ./audio_data/Healthy --quiet
```

## Output Files

When testing a directory, results are saved to a JSON file (default: `inference_results.json`)

Each prediction includes:
- `audio_file`: Path to the audio file
- `predicted_disease`: The predicted disease class
- `confidence`: Confidence score (0-1)
- `all_probabilities`: Probability for each disease class

Example JSON:
```json
[
  {
    "audio_file": "audio_data/Healthy/file_001.wav",
    "predicted_disease": "Bronchitis",
    "confidence": 0.3876,
    "all_probabilities": {
      "Healthy": 0.3402,
      "Cold Cough": 0.0327,
      "COVID-19": 0.0135,
      "Asthma": 0.2028,
      "Bronchitis": 0.3876,
      "Tuberculosis": 0.0127,
      "Pneumonia": 0.0105
    }
  }
]
```

## Tips

1. **Test on unseen data**: For accurate evaluation, test on audio files NOT used in training
2. **Use `--quiet` flag**: For faster feedback when testing large directories
3. **Check confidence scores**: Low confidence (<50%) indicates the model is uncertain
4. **Compare with validation set**: Test on different disease classes to see model's strengths/weaknesses

## Troubleshooting

**Error: "Model file not found"**
- Make sure `best_cough_classifier.pt` exists in the current directory
- Or specify the full path: `python test_model.py /path/to/best_cough_classifier.pt ...`

**Error: "No audio files found"**
- Check that audio files are `.wav` or `.mp3` format
- Ensure the directory path is correct
- Files in subdirectories are automatically found

**Slow inference**
- This is normal on CPU - each file takes ~1-2 seconds
- Use `--quiet` mode to reduce output overhead
- Consider using a GPU-enabled device if available

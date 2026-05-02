"""
Configuration file for the Cough Classifier model.
Centralized settings for easy customization.
"""

# ========================
# Audio Processing Settings
# ========================

# Sample rate for audio processing (Hz)
SAMPLE_RATE = 16000

# Number of mel-frequency cepstral coefficients
N_MELS = 64

# FFT window size
N_FFT = 400

# Hop length for STFT
HOP_LENGTH = 160

# Target duration for audio clips (seconds)
AUDIO_DURATION = 3

# ========================
# Model Architecture Settings
# ========================

# Number of output classes
NUM_CLASSES = 4

# Initial number of convolutional filters
INITIAL_FILTERS = 32

# Dropout rate for fully connected layers
FC_DROPOUT_1 = 0.5
FC_DROPOUT_2 = 0.3

# Number of neurons in hidden FC layers
FC_HIDDEN_1 = 128
FC_HIDDEN_2 = 64

# ========================
# Training Settings
# ========================

# Batch size for training
BATCH_SIZE = 16

# Initial learning rate
LEARNING_RATE = 0.001

# Learning rate scheduler factor
LR_SCHEDULER_FACTOR = 0.5

# Learning rate scheduler patience
LR_SCHEDULER_PATIENCE = 5

# Number of training epochs
NUM_EPOCHS = 50

# Early stopping patience
EARLY_STOPPING_PATIENCE = 10

# Train/validation split ratio
TRAIN_SPLIT = 0.8

# Optimizer (adam, sgd)
OPTIMIZER = "adam"

# Loss function (crossentropy, focal)
LOSS_FUNCTION = "crossentropy"

# ========================
# Data Settings
# ========================

# Path to training data directory
DATA_DIR = "audio_data"

# Supported audio file formats
SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.flac']

# Minimum samples per class (warning if below)
MIN_SAMPLES_PER_CLASS = 20

# Recommended samples per class
RECOMMENDED_SAMPLES_PER_CLASS = 100

# ========================
# Disease Classes
# ========================

DISEASE_CLASSES = {
    0: "Healthy",
    1: "Cold Cough",
    2: "COVID-19",
    3: "Asthma",
    4: "Bronchitis",
    5: "Tuberculosis",
    6: "Pneumonia"
}

# ========================
# Model Paths
# ========================

# Default model path
DEFAULT_MODEL_PATH = "cough_classifier.pt"

# Best model checkpoint path
BEST_MODEL_PATH = "best_cough_classifier.pt"

# ========================
# API Settings
# ========================

# Flask API host
API_HOST = "0.0.0.0"

# Flask API port
API_PORT = 5000

# Flask debug mode
API_DEBUG = False

# Maximum file upload size (bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# ========================
# Inference Settings
# ========================

# Confidence threshold for predictions
CONFIDENCE_THRESHOLD = 0.5

# Number of top predictions to return (when requested)
TOP_K = 3

# ========================
# Device Settings
# ========================

# Device to use ('cuda', 'cpu', or 'auto')
DEVICE = "auto"

# Number of workers for data loading
NUM_WORKERS = 4

# ========================
# Logging Settings
# ========================

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# Log file path
LOG_FILE = "cough_classifier.log"

# Enable file logging
FILE_LOGGING = True

# Enable console logging
CONSOLE_LOGGING = True

# ========================
# Evaluation Settings
# ========================

# Save confusion matrix
SAVE_CONFUSION_MATRIX = True

# Save class distribution plot
SAVE_CLASS_DISTRIBUTION = True

# Save per-class performance plot
SAVE_PER_CLASS_PERFORMANCE = True

# ========================
# Augmentation Settings (Future)
# ========================

# Enable data augmentation
ENABLE_AUGMENTATION = False

# Augmentation probability
AUGMENTATION_PROBABILITY = 0.5

# Mixup alpha
MIXUP_ALPHA = 0.2

# Time stretch range
TIME_STRETCH_RANGE = (0.9, 1.1)

# Pitch shift range (semitones)
PITCH_SHIFT_RANGE = (-2, 2)


def get_config():
    """
    Get all configuration settings as a dictionary.
    
    Returns:
        dict: All configuration settings
    """
    return {
        'audio': {
            'sample_rate': SAMPLE_RATE,
            'n_mels': N_MELS,
            'n_fft': N_FFT,
            'hop_length': HOP_LENGTH,
            'duration': AUDIO_DURATION,
        },
        'model': {
            'num_classes': NUM_CLASSES,
            'initial_filters': INITIAL_FILTERS,
            'fc_dropout_1': FC_DROPOUT_1,
            'fc_dropout_2': FC_DROPOUT_2,
            'fc_hidden_1': FC_HIDDEN_1,
            'fc_hidden_2': FC_HIDDEN_2,
        },
        'training': {
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE,
            'lr_scheduler_factor': LR_SCHEDULER_FACTOR,
            'lr_scheduler_patience': LR_SCHEDULER_PATIENCE,
            'num_epochs': NUM_EPOCHS,
            'early_stopping_patience': EARLY_STOPPING_PATIENCE,
            'train_split': TRAIN_SPLIT,
            'optimizer': OPTIMIZER,
            'loss_function': LOSS_FUNCTION,
        },
        'data': {
            'data_dir': DATA_DIR,
            'supported_formats': SUPPORTED_FORMATS,
            'min_samples_per_class': MIN_SAMPLES_PER_CLASS,
            'recommended_samples_per_class': RECOMMENDED_SAMPLES_PER_CLASS,
        },
        'disease_classes': DISEASE_CLASSES,
        'paths': {
            'default_model': DEFAULT_MODEL_PATH,
            'best_model': BEST_MODEL_PATH,
        },
        'api': {
            'host': API_HOST,
            'port': API_PORT,
            'debug': API_DEBUG,
            'max_file_size': MAX_FILE_SIZE,
        },
        'inference': {
            'confidence_threshold': CONFIDENCE_THRESHOLD,
            'top_k': TOP_K,
        },
        'device': {
            'device': DEVICE,
            'num_workers': NUM_WORKERS,
        },
    }


if __name__ == "__main__":
    import json
    config = get_config()
    print(json.dumps(config, indent=2))

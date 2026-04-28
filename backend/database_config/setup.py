#!/usr/bin/env python3
"""
Setup utility for the Cough Classifier project.
Handles initial setup, dependency installation, and data directory creation.

Usage:
    python setup.py
"""

import os
import sys
from pathlib import Path
import subprocess
import platform


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60 + "\n")


def print_step(number, text):
    """Print a numbered step."""
    print(f"[Step {number}] {text}")


def check_python_version():
    """Check if Python version is 3.8+."""
    print_step(1, "Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✓ Python {sys.version.split()[0]} detected")


def check_pip():
    """Check if pip is available."""
    print_step(2, "Checking pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✓ pip is available")
    except subprocess.CalledProcessError:
        print("❌ pip not found")
        sys.exit(1)


def install_dependencies():
    """Install required dependencies."""
    print_step(3, "Installing dependencies...")
    
    requirements_file = "requirements.txt"
    
    if not Path(requirements_file).exists():
        print(f"❌ {requirements_file} not found")
        return False
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            check=True
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_data_directories():
    """Create the audio_data directory structure."""
    print_step(4, "Creating data directories...")
    
    from backend.database_config.config import DISEASE_CLASSES
    
    data_dir = Path("audio_data")
    data_dir.mkdir(exist_ok=True)
    
    for disease_name in DISEASE_CLASSES.values():
        disease_dir = data_dir / disease_name
        disease_dir.mkdir(exist_ok=True)
        print(f"  ✓ Created: {disease_dir}")
    
    print("\n✓ Data directories created")
    print("\nPlease add your audio files in the following structure:")
    print("audio_data/")
    for disease_name in DISEASE_CLASSES.values():
        print(f"  ├── {disease_name}/")
        print(f"      └── *.wav (or *.mp3)")


def check_pytorch():
    """Check if PyTorch is properly installed."""
    print_step(5, "Checking PyTorch installation...")
    
    try:
        import torch
        import torchaudio
        
        print(f"✓ PyTorch {torch.__version__} detected")
        print(f"✓ Torchaudio {torchaudio.__version__} detected")
        
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠ CUDA not available (using CPU)")
        
        return True
    except ImportError as e:
        print(f"❌ PyTorch not properly installed: {e}")
        return False


def create_sample_data():
    """Optionally create sample data directories."""
    print_step(6, "Sample setup (optional)")
    
    response = input("Would you like to create sample data directories? (y/n): ").lower()
    if response == 'y':
        try:
            create_data_directories()
        except Exception as e:
            print(f"❌ Error creating directories: {e}")
    else:
        print("Skipped")


def print_completion_guide():
    """Print guide for next steps."""
    print_header("Setup Complete! ✓")
    
    print("Next steps:\n")
    print("1. Add your audio data:")
    print("   - Place audio files in audio_data/<disease_name>/ directories")
    print("   - Supported formats: .wav, .mp3, .m4a, .flac")
    print("   - Recommended: 100+ samples per class\n")
    
    print("2. Train the model:")
    print("   python train.py")
    print("   # or with custom parameters:")
    print("   python train.py --epochs 50 --batch-size 16\n")
    
    print("3. Make predictions:")
    print("   python inference.py <audio_file.wav>\n")
    
    print("4. Start the API server:")
    print("   python api.py\n")
    
    print("5. View examples:")
    print("   python examples.py\n")
    
    print("For more information, see:")
    print("  - README.md - Full documentation")
    print("  - QUICKSTART.md - Quick start guide")
    print("  - PROJECT_SUMMARY.md - Project overview")


def main():
    """Main setup function."""
    print_header("Cough Classifier - Setup")
    
    try:
        check_python_version()
        check_pip()
        install_dependencies()
        create_data_directories()
        check_pytorch()
        
        print_completion_guide()
        
        print("\n" + "="*60)
        print("Setup completed successfully! Happy training! 🎉")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

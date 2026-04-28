"""
Inference and evaluation utilities for the Cough Classifier model.
Provides convenient functions for making predictions and evaluating model performance.
"""

import torch
import torchaudio
import torchaudio.transforms as T
from pathlib import Path
from main import CoughClassifier, CoughClassifierTrainer, DISEASE_CLASSES, NUM_CLASSES
from main import SAMPLE_RATE, N_MELS, N_FFT, HOP_LENGTH
import json


class CoughInference:
    """Simplified inference interface for the trained cough classifier."""
    
    def __init__(self, model_path="cough_classifier.pt", device=None):
        """
        Initialize the inference engine.
        
        Args:
            model_path: Path to the saved model weights
            device: Device to use ('cuda' or 'cpu')
        """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        self.model = CoughClassifier(num_classes=NUM_CLASSES)
        self.trainer = CoughClassifierTrainer(self.model, device=self.device)
        self.model_path = Path(model_path)
        self.model_loaded = False
        
        if self.model_path.exists():
            self.trainer.load_model(str(self.model_path))
            self.model_loaded = True
            print(f"Model loaded from {self.model_path}")
        else:
            print(f"Warning: Model file {self.model_path} not found. Inference will use mock mode in the API.")
    
    def classify_audio(self, audio_path):
        """
        Classify a single audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            dict: Classification results including disease, confidence, and probabilities
        """
        disease, confidence, probs = self.trainer.predict(audio_path)
        
        return {
            "audio_file": str(audio_path),
            "predicted_disease": disease,
            "confidence": confidence,
            "all_probabilities": {
                cls: float(prob) for cls, prob in probs.items()
            }
        }
    
    def classify_multiple(self, audio_directory, max_files=None):
        """
        Classify all audio files in a directory.
        
        Args:
            audio_directory: Path to directory containing audio files
            max_files: Optional cap on how many files to classify
            
        Returns:
            list: Classification results for all files
        """
        audio_dir = Path(audio_directory)
        results = []
        
        # Find all audio files
        audio_files = list(audio_dir.glob("**/*.wav")) + list(audio_dir.glob("**/*.mp3"))
        if max_files is not None and max_files > 0:
            audio_files = audio_files[:max_files]
        
        print(f"Found {len(audio_files)} audio files")
        
        for audio_file in audio_files:
            try:
                result = self.classify_audio(str(audio_file))
                results.append(result)
                print(f"✓ {audio_file.name}: {result['predicted_disease']} ({result['confidence']:.1%})")
            except Exception as e:
                print(f"✗ Error processing {audio_file.name}: {e}")
        
        return results
    
    def save_results(self, results, output_file="predictions.json"):
        """
        Save classification results to a JSON file.
        
        Args:
            results: List of classification results
            output_file: Path to save the results
        """
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    
    def get_top_predictions(self, audio_path, top_k=3):
        """
        Get the top-k predictions for an audio file.
        
        Args:
            audio_path: Path to the audio file
            top_k: Number of top predictions to return
            
        Returns:
            list: Top-k predictions with confidence scores
        """
        disease, confidence, probs = self.trainer.predict(audio_path)
        
        sorted_probs = sorted(
            probs.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_probs[:top_k]


def batch_classify_test_set(test_directory, model_path="cough_classifier.pt"):
    """
    Utility function to classify all files in a test directory.
    
    Args:
        test_directory: Path to directory with test audio files
        model_path: Path to the trained model
    """
    inference = CoughInference(model_path)
    results = inference.classify_multiple(test_directory)
    inference.save_results(results, "test_predictions.json")
    
    # Print summary
    if results:
        total = len(results)
        diseases = {}
        for result in results:
            disease = result["predicted_disease"]
            diseases[disease] = diseases.get(disease, 0) + 1
        
        print("\n" + "="*50)
        print("Classification Summary")
        print("="*50)
        for disease, count in sorted(diseases.items()):
            print(f"{disease}: {count} files ({(count/total)*100:.1f}%)")


if __name__ == "__main__":
    # Example: Classify all audio files in the default 'audio_data' directory
    # This directory is created when you run `download_dataset.py`
    print("Running batch classification on 'audio_data' directory...")
    batch_classify_test_set("audio_data")

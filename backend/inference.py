"""
Inference and evaluation utilities for the Cough Classifier model.
Provides convenient functions for making predictions and evaluating model performance.
"""

import json
import os
from pathlib import Path

import torch
import torchaudio
import torchaudio.transforms as T

from main import CoughClassifier, CoughClassifierTrainer, DISEASE_CLASSES, NUM_CLASSES
from main import SAMPLE_RATE, N_MELS, N_FFT, HOP_LENGTH


def _candidate_model_paths(explicit_path: str | None = None) -> list[Path]:
    """Return likely checkpoint locations in priority order."""
    backend_dir = Path(__file__).resolve().parent
    repo_root = backend_dir.parent

    candidates: list[Path] = []
    seen: set[str] = set()

    def add(path: Path) -> None:
        resolved_key = str(path.resolve()) if path.exists() else str(path)
        if resolved_key not in seen:
            seen.add(resolved_key)
            candidates.append(path)

    if explicit_path:
        add(Path(explicit_path).expanduser())

    env_path = os.getenv("MODEL_PATH", "").strip()
    if env_path:
        add(Path(env_path).expanduser())

    # Prefer the strongest checkpoint shipped with the repo, then fall back to
    # alternate checkpoints and the legacy backend-local filename.
    for candidate in [
        repo_root / "best_cough_classifier.pt",
        repo_root / "balanced_best_cough_classifier.pt",
        repo_root / "capped_best_cough_classifier.pt",
        repo_root / "balanced_cough_classifier.pt",
        repo_root / "capped_cough_classifier.pt",
        repo_root / "best_try.pt",
        repo_root / "test_augmented.pt",
        backend_dir / "cough_classifier.pt",
    ]:
        add(candidate)

    return candidates


def resolve_model_path(model_path: str | None = None) -> Path | None:
    """Resolve the first existing checkpoint path from the candidate list."""
    for candidate in _candidate_model_paths(model_path):
        if candidate.exists():
            return candidate
    return None


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
        self.model_path = resolve_model_path(model_path) or Path(model_path)
        self.model_loaded = False
        
        if self.model_path.exists():
            try:
                self.trainer.load_model(str(self.model_path))
                self.model_loaded = True
                print(f"Model loaded from {self.model_path}")
            except Exception as exc:
                print(f"Warning: Failed to load model from {self.model_path}: {exc}")
                alternate_path = next(
                    (candidate for candidate in _candidate_model_paths(None) if candidate.exists() and candidate != self.model_path),
                    None,
                )
                if alternate_path is not None:
                    try:
                        self.model_path = alternate_path
                        self.trainer.load_model(str(self.model_path))
                        self.model_loaded = True
                        print(f"Model loaded from fallback path {self.model_path}")
                    except Exception as fallback_exc:
                        print(f"Warning: Fallback model load failed: {fallback_exc}")
                if not self.model_loaded:
                    print("Warning: Model checkpoint could not be loaded. Inference will use mock mode in the API.")
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

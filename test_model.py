#!/usr/bin/env python3
"""
Simple test script to run inference on unseen audio data using the trained model.
Usage: python test_model.py <model_path> <audio_path_or_directory>
"""

import sys
import argparse
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from inference import CoughInference

def main():
    parser = argparse.ArgumentParser(description="Test the trained cough classifier on unseen data")
    parser.add_argument("model_path", help="Path to the trained model (e.g., best_cough_classifier.pt)")
    parser.add_argument("data_path", help="Path to audio file or directory of audio files to test")
    parser.add_argument("--output", default="inference_results.json", help="Output JSON file for results")
    parser.add_argument("--device", default=None, help="Device to use (cuda or cpu)")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-file output, only show summary")
    parser.add_argument("--max-files", type=int, default=None, help="Limit the number of files tested from a directory")
    
    args = parser.parse_args()
    
    # Initialize inference engine
    print(f"Loading model from {args.model_path}...")
    inference = CoughInference(args.model_path, device=args.device)
    
    if not inference.model_loaded:
        print("Error: Failed to load model")
        return 1
    
    data_path = Path(args.data_path)
    
    # Test single file
    if data_path.is_file():
        print(f"\nTesting single file: {data_path.name}")
        print("-" * 60)
        result = inference.classify_audio(str(data_path))
        print(f"File: {result['audio_file']}")
        print(f"Predicted Disease: {result['predicted_disease']}")
        print(f"Confidence: {result['confidence']:.1%}")
        print("\nAll Class Probabilities:")
        for disease, prob in sorted(result['all_probabilities'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {disease:20s}: {prob:.4f}")
    
    # Test directory
    elif data_path.is_dir():
        print(f"\nTesting all audio files in: {data_path}")
        print("-" * 60)
        
        # Redirect stdout during classify_multiple if quiet mode
        import io
        import contextlib
        
        if args.quiet:
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                results = inference.classify_multiple(str(data_path), max_files=args.max_files)
        else:
            results = inference.classify_multiple(str(data_path), max_files=args.max_files)
        
        if results:
            # Save results
            inference.save_results(results, args.output)
            
            # Print summary
            print("\n" + "=" * 60)
            print("CLASSIFICATION SUMMARY")
            print("=" * 60)
            total = len(results)
            diseases = {}
            for result in results:
                disease = result["predicted_disease"]
                diseases[disease] = diseases.get(disease, 0) + 1
            
            for disease in sorted(diseases.keys()):
                count = diseases[disease]
                percentage = (count / total) * 100
                print(f"{disease:20s}: {count:4d} files ({percentage:5.1f}%)")
            
            print(f"\nTotal files tested: {total}")
            print(f"Results saved to: {args.output}")
    
    else:
        print(f"Error: {args.data_path} is not a valid file or directory")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

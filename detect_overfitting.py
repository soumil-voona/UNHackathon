#!/usr/bin/env python3
"""
Overfitting Detection Script
Tests model on different data sources to check for overfitting.
Compares predictions across different classes to measure generalization.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent / 'backend'))
from inference import CoughInference

def analyze_predictions(results):
    """Analyze prediction results to detect overfitting signs."""
    if not results:
        return None
    
    # Group by predicted disease
    predictions_by_disease = defaultdict(int)
    confidence_by_disease = defaultdict(list)
    correct_predictions = 0
    total_predictions = len(results)
    
    for result in results:
        pred_disease = result['predicted_disease']
        confidence = result['confidence']
        
        predictions_by_disease[pred_disease] += 1
        confidence_by_disease[pred_disease].append(confidence)
    
    # Calculate statistics
    stats = {
        'total_files': total_predictions,
        'avg_confidence': sum(r['confidence'] for r in results) / total_predictions,
        'max_confidence': max(r['confidence'] for r in results),
        'min_confidence': min(r['confidence'] for r in results),
        'predictions_by_disease': dict(predictions_by_disease),
        'avg_confidence_by_disease': {
            disease: sum(confs) / len(confs) 
            for disease, confs in confidence_by_disease.items()
        }
    }
    
    return stats

def print_analysis(test_name, stats):
    """Print formatted analysis of predictions."""
    if not stats:
        return
    
    print("\n" + "=" * 70)
    print(f"OVERFITTING ANALYSIS: {test_name}")
    print("=" * 70)
    print(f"Total files tested: {stats['total_files']}")
    print(f"Average confidence: {stats['avg_confidence']:.1%}")
    print(f"Confidence range: {stats['min_confidence']:.1%} - {stats['max_confidence']:.1%}")
    
    print("\nPredictions by Disease:")
    for disease in sorted(stats['predictions_by_disease'].keys()):
        count = stats['predictions_by_disease'][disease]
        pct = (count / stats['total_files']) * 100
        avg_conf = stats['avg_confidence_by_disease'][disease]
        print(f"  {disease:20s}: {count:4d} files ({pct:5.1f}%) - Avg confidence: {avg_conf:.1%}")
    
    print("\n" + "=" * 70)
    
    # Overfitting indicators
    print("OVERFITTING INDICATORS:")
    if stats['avg_confidence'] > 0.95:
        print("  ⚠️  WARNING: Very high average confidence (>95%) - possible overfitting")
    elif stats['avg_confidence'] < 0.60:
        print("  ⚠️  WARNING: Low average confidence (<60%) - model uncertainty")
    else:
        print("  ✓ Confidence level appears reasonable (60-95%)")
    
    # Check for class bias
    max_class_pct = max((count / stats['total_files']) * 100 
                        for count in stats['predictions_by_disease'].values())
    if max_class_pct > 80:
        print(f"  ⚠️  WARNING: Model heavily biased towards one class ({max_class_pct:.1f}%)")
    else:
        print("  ✓ Predictions reasonably distributed across classes")

def main():
    print("\n" + "=" * 70)
    print("OVERFITTING DETECTION TOOL")
    print("=" * 70)
    
    model_path = "best_cough_classifier.pt"
    
    # Check if model exists
    if not Path(model_path).exists():
        print(f"Error: {model_path} not found")
        print("Make sure you're in the project root directory")
        return 1
    
    print(f"\nLoading model from {model_path}...")
    inference = CoughInference(model_path)
    
    if not inference.model_loaded:
        print("Error: Failed to load model")
        return 1
    
    test_results = {}
    
    # Test on each available disease class
    audio_data_dir = Path("audio_data")
    if audio_data_dir.exists():
        print("\nTesting on training data classes (to check memorization)...")
        print("-" * 70)
        
        for class_dir in sorted(audio_data_dir.iterdir()):
            if class_dir.is_dir() and not class_dir.name.startswith('.'):
                class_name = class_dir.name
                print(f"\n  Testing {class_name}...", end=" ", flush=True)
                
                results = inference.classify_multiple(str(class_dir))
                stats = analyze_predictions(results)
                test_results[f"Training_Class_{class_name}"] = stats
                
                print(f"({len(results)} files)")
    
    # Print detailed analysis
    print("\n\n")
    for test_name, stats in test_results.items():
        if stats:
            print_analysis(test_name, stats)
    
    # Summary recommendation
    print("\n" + "=" * 70)
    print("OVERFITTING SUMMARY")
    print("=" * 70)
    
    avg_confidences = [s['avg_confidence'] for s in test_results.values() if s]
    if avg_confidences:
        overall_avg = sum(avg_confidences) / len(avg_confidences)
        
        if overall_avg > 0.95:
            print("\n❌ LIKELY OVERFITTING DETECTED")
            print("   Model shows suspiciously high confidence across all classes.")
            print("   Consider:")
            print("   - Increasing data augmentation strength")
            print("   - Reducing model size further")
            print("   - Adding more dropout")
            print("   - Using external validation data")
        elif overall_avg > 0.85:
            print("\n⚠️  POSSIBLE SLIGHT OVERFITTING")
            print("   Model confidence is quite high. Monitor with external test data.")
            print("   Recommendation: Test on completely new datasets from Kaggle")
        else:
            print("\n✅ MODEL APPEARS WELL-GENERALIZED")
            print("   Confidence levels are reasonable.")
            print("   Model likely generalizes well to unseen data.")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("  1. For true overfitting detection, test on completely new data:")
    print("     kaggle datasets download -d ruchikashirsath/tb-audio")
    print("     python test_model.py best_cough_classifier.pt ./tb-audio/")
    print("\n  2. Compare results across different datasets")
    print("  3. If accuracy drops >20%, investigate overfitting")
    print("=" * 70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

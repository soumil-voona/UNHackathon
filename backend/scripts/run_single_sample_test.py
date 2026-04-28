from inference import CoughInference
from pathlib import Path
import json

inf = CoughInference(model_path='../best_cough_classifier.pt')
root = Path('../audio_data')
results = []

for class_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
    files = list(class_dir.glob('**/*.wav')) + list(class_dir.glob('**/*.WAV')) + list(class_dir.glob('**/*.webm'))
    if not files:
        print(f"No audio files found in {class_dir}")
        continue
    sample = files[0]
    try:
        res = inf.classify_audio(str(sample))
        res['expected_class'] = class_dir.name
        results.append(res)
        print(f"{class_dir.name}: predicted={res['predicted_disease']} ({res['confidence']:.1%}) file={sample.name}")
    except Exception as e:
        print(f"Error classifying {sample}: {e}")

out = Path('single_sample_predictions.json')
out.write_text(json.dumps(results, indent=2))
print('\nSaved results to', out)

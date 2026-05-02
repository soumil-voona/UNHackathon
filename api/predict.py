"""
Vercel Serverless API endpoint for /api/predict
Wraps the FastAPI predict endpoint for Vercel deployment
"""

import os
import sys
import json
import time
from pathlib import Path
from urllib.request import urlretrieve
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import torch
from io import BytesIO
import base64

# Import inference after path setup
try:
    from main import CoughClassifier, CoughClassifierTrainer, DISEASE_CLASSES, NUM_CLASSES
    from main import SAMPLE_RATE, N_MELS, N_FFT, HOP_LENGTH
    from inference import CoughInference
    MODEL_PATH = Path(__file__).parent.parent / "best_cough_classifier.pt"
    if not MODEL_PATH.exists():
        MODEL_PATH = backend_path / "cough_classifier.pt"
    
    INFERENCE = CoughInference(model_path=str(MODEL_PATH))
    MODEL_LOADED = INFERENCE.model_loaded
except Exception as e:
    log.warning(f"Could not load model: {e}")
    INFERENCE = None
    MODEL_LOADED = False


def mock_classify(audio_data: bytes) -> dict:
    """Mock classifier for demo"""
    import random
    
    file_hash = hash(audio_data) % 1000
    rng = random.Random(file_hash)
    
    dominant_idx = rng.randint(0, len(DISEASE_CLASSES) - 1)
    dominant_prob = rng.uniform(0.45, 0.80)
    
    remaining = 1.0 - dominant_prob
    others = [i for i in range(len(DISEASE_CLASSES)) if i != dominant_idx]
    splits = sorted([rng.random() for _ in range(len(others) - 1)])
    splits = [0.0] + splits + [1.0]
    other_probs = [remaining * (splits[i + 1] - splits[i]) for i in range(len(others))]
    
    all_probs = {}
    for i, name in DISEASE_CLASSES.items():
        if i == dominant_idx:
            all_probs[name] = round(dominant_prob, 4)
        else:
            idx_in_others = others.index(i)
            all_probs[name] = round(other_probs[idx_in_others], 4)
    
    predicted_disease = DISEASE_CLASSES[dominant_idx]
    confidence = dominant_prob
    
    return {
        "predicted_disease": predicted_disease,
        "confidence": round(confidence, 4),
        "all_probabilities": all_probs,
        "mock": True,
    }


def handler(request):
    """Handle POST /api/predict requests"""
    
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }
    
    start_time = time.time()
    
    try:
        # Get the audio file from the request
        content_type = request.headers.get("content-type", "")
        
        if "multipart/form-data" in content_type:
            # Handle multipart form data
            if "files" not in request.files:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "No audio file provided"})
                }
            
            audio_file = request.files["files"][0]
            audio_data = audio_file.read()
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Request must be multipart/form-data"})
            }
        
        # Save and classify
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        try:
            if MODEL_LOADED and INFERENCE:
                result = INFERENCE.classify_audio(tmp_path)
            else:
                result = mock_classify(audio_data)
            
            processing_time = time.time() - start_time
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": True,
                    "prediction": result,
                    "processing_time": round(processing_time, 2)
                })
            }
        finally:
            # Cleanup temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
                
    except Exception as e:
        log.error(f"Error in predict endpoint: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

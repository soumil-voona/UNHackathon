"""
Vercel Serverless API endpoint for /api/health
Health check endpoint
"""

import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    import torch
    from inference import CoughInference
    
    MODEL_PATH = Path(__file__).parent.parent / "best_cough_classifier.pt"
    if not MODEL_PATH.exists():
        MODEL_PATH = backend_path / "cough_classifier.pt"
    
    INFERENCE = CoughInference(model_path=str(MODEL_PATH))
    MODEL_LOADED = INFERENCE.model_loaded
    DEVICE = str(INFERENCE.trainer.device)
except Exception as e:
    MODEL_LOADED = False
    DEVICE = "cpu"


def handler(request):
    """Handle GET /api/health requests"""
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "status": "healthy",
            "model_loaded": MODEL_LOADED,
            "mock_mode": not MODEL_LOADED,
            "device": DEVICE,
            "service": "CoughNet API"
        })
    }

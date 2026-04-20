"""
FastAPI for the Cough Classifier model.
Provides REST endpoints for audio classification.

Installation: pip install fastapi uvicorn python-dotenv python-multipart

Usage:
    python api.py
    
Then access:
    POST http://localhost:8000/predict - Upload audio file for classification
    GET http://localhost:8000/health - Check API health
    GET http://localhost:8000/classes - Get available disease classes
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import torch
from inference import CoughInference
import os
import shutil
from urllib.request import urlretrieve
import time

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'webm', 'ogg'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
UPLOAD_FOLDER = 'uploads'

# Create upload folder if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Initialize inference engine
try:
    inference = CoughInference(model_path="cough_classifier.pt")
    model_loaded = True
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    inference = None
    model_loaded = False


class PredictionResponse(BaseModel):
    success: bool
    prediction: dict


class TopPredictionsResponse(BaseModel):
    success: bool
    top_predictions: list


class URLPredictionRequest(BaseModel):
    url: str


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get('/health')
def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "model_loaded": model_loaded,
        "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    })


@app.get('/classes')
def get_classes():
    """Get available disease classes."""
    from main import DISEASE_CLASSES
    return JSONResponse({
        "classes": DISEASE_CLASSES,
        "count": len(DISEASE_CLASSES)
    })


@app.post('/predict')
async def predict(audio: UploadFile = File(...)):
    """Predict disease from uploaded audio file."""
    start_time = time.time()
    
    if not model_loaded:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Please ensure cough_classifier.pt exists."
        )
    
    print(f"\n[PREDICT] Received: {audio.filename} ({audio.content_type})")
    
    if not allowed_file(audio.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}. Received: {audio.filename}"
        )
    
    filepath = None
    try:
        # Save uploaded file
        filepath = os.path.join(UPLOAD_FOLDER, audio.filename)
        with open(filepath, "wb") as f:
            contents = await audio.read()
            f.write(contents)
        
        save_time = time.time() - start_time
        print(f"[PREDICT] Saved in {save_time:.2f}s")
        
        # Make prediction
        print(f"[PREDICT] Starting inference...")
        inference_start = time.time()
        result = inference.classify_audio(filepath)
        inference_time = time.time() - inference_start
        print(f"[PREDICT] Inference: {inference_time:.2f}s")
        print(f"[PREDICT] Result: {result}")
        
        total_time = time.time() - start_time
        print(f"[PREDICT] Total: {total_time:.2f}s\n")
        
        return JSONResponse({
            "success": True,
            "prediction": result,
            "processing_time": total_time
        })
    
    except Exception as e:
        print(f"[PREDICT] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing audio: {str(e)}"}
        )
    finally:
        # Clean up
        if filepath and os.path.exists(filepath):
            os.remove(filepath)


@app.post('/predict-url')
async def predict_url(request_data: URLPredictionRequest):
    """Predict disease from audio URL."""
    
    if not model_loaded:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Please ensure cough_classifier.pt exists."
        )
    
    try:
        # Download file
        filename = os.path.basename(request_data.url).split('?')[0]
        if not filename:
            filename = "audio.wav"
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        urlretrieve(request_data.url, filepath)
        
        # Make prediction
        result = inference.classify_audio(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return JSONResponse({
            "success": True,
            "prediction": result
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing audio URL: {str(e)}"}
        )


@app.post('/top-predictions')
async def get_top_predictions(audio: UploadFile = File(...), top_k: int = 3):
    """Get top-k predictions for uploaded audio file."""
    
    if not model_loaded:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Please ensure cough_classifier.pt exists."
        )
    
    if not allowed_file(audio.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        filepath = os.path.join(UPLOAD_FOLDER, audio.filename)
        with open(filepath, "wb") as f:
            contents = await audio.read()
            f.write(contents)
        
        top_preds = inference.get_top_predictions(filepath, top_k=top_k)
        
        os.remove(filepath)
        
        return JSONResponse({
            "success": True,
            "top_predictions": [
                {
                    "disease": pred[0],
                    "confidence": float(pred[1])
                }
                for pred in top_preds
            ]
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing audio: {str(e)}"}
        )


@app.get('/')
def index():
    """API documentation."""
    return JSONResponse({
        "name": "Cough Classifier API",
        "version": "1.0.0",
        "endpoints": {
            "/health": {
                "method": "GET",
                "description": "Check API health and model status"
            },
            "/classes": {
                "method": "GET",
                "description": "Get available disease classes"
            },
            "/predict": {
                "method": "POST",
                "description": "Classify cough from uploaded audio file",
                "parameters": {
                    "audio": "Audio file (wav, mp3, m4a, flac)"
                }
            },
            "/predict-url": {
                "method": "POST",
                "description": "Classify cough from audio URL",
                "parameters": {
                    "url": "URL to audio file"
                }
            },
            "/top-predictions": {
                "method": "POST",
                "description": "Get top-k predictions for audio file",
                "parameters": {
                    "audio": "Audio file (wav, mp3, m4a, flac)",
                    "top_k": "Number of top predictions (default: 3)"
                }
            }
        }
    })


if __name__ == '__main__':
    import uvicorn
    print("Starting Cough Classifier API...")
    print(f"Model loaded: {model_loaded}")
    print(f"Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
    print("\nAPI Documentation: http://localhost:8000/")
    print("Interactive Docs: http://localhost:8000/docs")
    uvicorn.run(app, host='0.0.0.0', port=8000)

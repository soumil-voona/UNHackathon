"""
CoughNet FastAPI Backend
========================
REST API for cough-based health issue classification.

Endpoints:
    POST /predict          - Upload audio file for disease classification
    POST /predict-url      - Classify audio from a URL
    POST /top-predictions  - Get top-k predictions for an audio file
    GET  /health           - Health check and model status
    GET  /classes          - Available disease classes
    GET  /                 - API documentation

Installation:
    pip install -r requirements.txt

Usage:
    python api.py
    # Then open: http://localhost:8000/docs

The server runs on port 8000 by default and accepts requests from any origin (CORS enabled).
If the trained model file (cough_classifier.pt) is not present, the server falls back to a
rule-based mock classifier so the app remains fully runnable for demos.
"""

import os
import time
import random
import traceback
import logging
import sys
from pathlib import Path
from urllib.request import urlretrieve

import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add backend directory to path so imports work from root-level module execution
sys.path.insert(0, str(Path(__file__).parent))

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("coughnet")

# ---------------------------------------------------------------------------
# App & CORS
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CoughNet API",
    description="Cough-based respiratory health classification API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {"wav", "webm"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

log.info(f"Upload folder: {UPLOAD_FOLDER.absolute()}")

# Disease classes (mirrors main.py DISEASE_CLASSES)
DISEASE_CLASSES = {
    0: "Healthy",
    1: "COVID-19",
    2: "Bronchitis",
    3: "Tuberculosis",
}

# ---------------------------------------------------------------------------
# Model loading — graceful fallback to mock classifier
# ---------------------------------------------------------------------------
model_loaded = False
inference = None
# Resolve model path from env, then fall back to repository defaults.
env_model_path = os.getenv("MODEL_PATH", "").strip()
if env_model_path:
    MODEL_PATH = Path(env_model_path)
else:
    MODEL_PATH = Path(__file__).parent.parent / "best_cough_classifier.pt"
    if not MODEL_PATH.exists():
        MODEL_PATH = Path(__file__).parent / "cough_classifier.pt"

try:
    from inference import CoughInference
    inference = CoughInference(model_path=str(MODEL_PATH))
    if inference.model_loaded:
        device = inference.trainer.device
        log.info(f"Trained model loaded on device: {device}")
        log.info(f"  GPU available: {torch.cuda.is_available()}")
        model_loaded = True
    else:
        inference = None
        model_loaded = False
        log.warning(
            "Model checkpoint not found. Falling back to mock (rule-based) classifier. "
            f"Expected checkpoint at: {MODEL_PATH}"
        )
except Exception as e:
    log.warning(
        f"Could not load trained model ({e}). "
        "Falling back to mock (rule-based) classifier. "
        f"Expected checkpoint at: {MODEL_PATH}"
    )


# ---------------------------------------------------------------------------
# Mock / simulated AI classifier
# ---------------------------------------------------------------------------

def mock_classify(audio_path: str) -> dict:
    """
    Rule-based mock classifier used when the trained model is not available.

    Simulates realistic probability distributions so the frontend demo works
    end-to-end without requiring a trained model file.  Replace this function
    with a real model call when cough_classifier.pt is available.

    The distribution is seeded from the file size so repeated calls with the
    same recording produce consistent results within a session.
    """
    try:
        file_size = Path(audio_path).stat().st_size
    except OSError:
        file_size = 42

    rng = random.Random(file_size % 1000)

    # Pick a dominant class and assign it a high probability
    dominant_idx = rng.randint(0, len(DISEASE_CLASSES) - 1)
    dominant_prob = rng.uniform(0.45, 0.80)

    # Distribute the remaining probability mass among the other classes
    remaining = 1.0 - dominant_prob
    others = [i for i in range(len(DISEASE_CLASSES)) if i != dominant_idx]
    splits = sorted([rng.random() for _ in range(len(others) - 1)])
    splits = [0.0] + splits + [1.0]
    other_probs = [remaining * (splits[i + 1] - splits[i]) for i in range(len(others))]

    all_probs: dict = {}
    for i, name in DISEASE_CLASSES.items():
        if i == dominant_idx:
            all_probs[name] = round(dominant_prob, 4)
        else:
            idx_in_others = others.index(i)
            all_probs[name] = round(other_probs[idx_in_others], 4)

    predicted_disease = DISEASE_CLASSES[dominant_idx]
    confidence = dominant_prob

    log.info(f"[MOCK] Predicted: {predicted_disease} ({confidence:.1%})")

    return {
        "audio_file": str(audio_path),
        "predicted_disease": predicted_disease,
        "confidence": confidence,
        "all_probabilities": all_probs,
        "mock": True,
    }


def classify_audio(audio_path: str) -> dict:
    """
    Dispatch to the real model or the mock classifier.

    This is the single integration point: swap out mock_classify for a
    different model (TensorFlow.js, OpenAI Whisper, external API, etc.)
    by replacing the else branch below.
    """
    if model_loaded and inference is not None:
        return inference.classify_audio(audio_path)
    else:
        return mock_classify(audio_path)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    """Return True if the filename has an allowed audio extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class URLPredictionRequest(BaseModel):
    url: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    """API documentation overview."""
    return JSONResponse({
        "name": "CoughNet API",
        "version": "1.0.0",
        "model_loaded": model_loaded,
        "endpoints": {
            "GET  /health": "Health check and model status",
            "GET  /classes": "Available disease classes",
            "POST /predict": "Classify cough from uploaded audio file",
            "POST /predict-url": "Classify cough from audio URL",
            "POST /top-predictions": "Get top-k predictions for audio file",
        },
    })


@app.get("/health")
def health_check():
    """Health check — returns model status and device info."""
    return JSONResponse({
        "status": "healthy",
        "model_loaded": model_loaded,
        "mock_mode": not model_loaded,
        "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu")),
    })


@app.get("/classes")
def get_classes():
    """Return the list of disease classes the model can predict."""
    return JSONResponse({
        "classes": DISEASE_CLASSES,
        "count": len(DISEASE_CLASSES),
    })


@app.post("/predict")
async def predict(audio: UploadFile = File(...)):
    """
    Classify a cough recording.

    Accepts WAV directly, and WebM via temporary conversion for inference.
    Returns a JSON object with the predicted disease, confidence score,
    and the full probability distribution across all classes.

    Example response:
        {
            "success": true,
            "prediction": {
                "predicted_disease": "Healthy",
                "confidence": 0.72,
                "all_probabilities": { "Healthy": 0.72, "Cold Cough": 0.08, ... }
            },
            "processing_time": 0.43
        }
    """
    start_time = time.time()
    filepath = None

    log.info(f"[PREDICT] Received: {audio.filename!r} ({audio.content_type})")

    # Validate file extension
    if not allowed_file(audio.filename or ""):
        raise HTTPException(
            status_code=400,
            detail=(
                f"File type not allowed. "
                f"Accepted types: {', '.join(sorted(ALLOWED_EXTENSIONS))}. "
                f"Got: {audio.filename!r}"
            ),
        )

    try:
        # ----------------------------------------------------------------
        # 1. Save the uploaded file to disk
        # ----------------------------------------------------------------
        safe_name = Path(audio.filename).name  # strip any path components
        filepath = UPLOAD_FOLDER / safe_name
        log.info(f"[PREDICT] Saving to: {filepath.absolute()}")

        contents = await audio.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB.",
            )

        with open(filepath, "wb") as f:
            f.write(contents)

        file_size = filepath.stat().st_size
        log.info(f"[PREDICT] Saved {file_size:,} bytes in {time.time() - start_time:.2f}s")

        # ----------------------------------------------------------------
        # 2. Run classification (real model or mock)
        # ----------------------------------------------------------------
        log.info("[PREDICT] Starting inference...")
        inference_start = time.time()
        result = classify_audio(str(filepath.absolute()))
        log.info(f"[PREDICT] Inference done in {time.time() - inference_start:.2f}s")
        log.info(f"[PREDICT] Result: {result['predicted_disease']} ({result['confidence']:.1%})")

        total_time = time.time() - start_time
        log.info(f"[PREDICT] Total: {total_time:.2f}s")

        return JSONResponse({
            "success": True,
            "prediction": result,
            "processing_time": round(total_time, 3),
        })

    except HTTPException:
        raise  # re-raise validation errors unchanged

    except Exception as e:
        error_trace = traceback.format_exc()
        log.error(f"[PREDICT] ERROR: {e}\n{error_trace}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error processing audio: {str(e)}",
                "type": type(e).__name__,
            },
        )

    finally:
        # ----------------------------------------------------------------
        # 3. Always clean up the uploaded file
        # ----------------------------------------------------------------
        if filepath and filepath.exists():
            try:
                filepath.unlink()
                log.info(f"[PREDICT] Cleaned up: {filepath.name}")
            except Exception as cleanup_err:
                log.warning(f"[PREDICT] Could not delete {filepath}: {cleanup_err}")


@app.post("/predict-url")
async def predict_url(request_data: URLPredictionRequest):
    """
    Classify a cough recording from a remote URL.

    The server downloads the file, runs classification, then deletes the file.
    """
    filepath = None
    try:
        filename = Path(request_data.url.split("?")[0]).name or "audio.wav"
        filepath = UPLOAD_FOLDER / filename
        log.info(f"[PREDICT-URL] Downloading: {request_data.url}")
        urlretrieve(request_data.url, filepath)

        result = classify_audio(str(filepath))

        return JSONResponse({"success": True, "prediction": result})

    except Exception as e:
        log.error(f"[PREDICT-URL] ERROR: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error processing audio URL: {str(e)}"},
        )

    finally:
        if filepath and filepath.exists():
            try:
                filepath.unlink()
            except Exception:
                pass


@app.post("/top-predictions")
async def get_top_predictions(audio: UploadFile = File(...), top_k: int = 3):
    """
    Return the top-k most likely diseases for an uploaded audio file.

    Useful for displaying a ranked list in the frontend.
    """
    filepath = None
    try:
        if not allowed_file(audio.filename or ""):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        safe_name = Path(audio.filename).name
        filepath = UPLOAD_FOLDER / safe_name
        with open(filepath, "wb") as f:
            f.write(await audio.read())

        result = classify_audio(str(filepath))
        probs = result.get("all_probabilities", {})

        top_preds = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return JSONResponse({
            "success": True,
            "top_predictions": [
                {"disease": disease, "confidence": round(float(conf), 4)}
                for disease, conf in top_preds
            ],
        })

    except HTTPException:
        raise

    except Exception as e:
        log.error(f"[TOP-PREDICT] ERROR: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error processing audio: {str(e)}"},
        )

    finally:
        if filepath and filepath.exists():
            try:
                filepath.unlink()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    log.info("=" * 60)
    log.info("Starting CoughNet API")
    log.info(f"  Model loaded : {model_loaded}")
    log.info(f"  Mock mode    : {not model_loaded}")
    log.info(f"  Device       : {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
    log.info("=" * 60)
    log.info("API docs : http://localhost:8000/docs")
    log.info("Health   : http://localhost:8000/health")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

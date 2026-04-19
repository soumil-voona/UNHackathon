"""
Flask API for the Cough Classifier model.
Provides REST endpoints for audio classification.

Installation: pip install flask flask-cors python-dotenv

Usage:
    python api.py
    
Then access:
    POST http://localhost:5000/predict - Upload audio file for classification
    GET http://localhost:5000/health - Check API health
    GET http://localhost:5000/classes - Get available disease classes
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import torch
from inference import CoughInference
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
UPLOAD_FOLDER = 'uploads'

# Create upload folder if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize inference engine
try:
    inference = CoughInference(model_path="cough_classifier.pt")
    model_loaded = True
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    inference = None
    model_loaded = False


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": model_loaded,
        "device": str(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
    }), 200


@app.route('/classes', methods=['GET'])
def get_classes():
    """Get available disease classes."""
    from main import DISEASE_CLASSES
    return jsonify({
        "classes": DISEASE_CLASSES,
        "count": len(DISEASE_CLASSES)
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    """Predict disease from uploaded audio file."""
    
    if not model_loaded:
        return jsonify({
            "error": "Model not loaded. Please ensure cough_classifier.pt exists."
        }), 500
    
    # Check if file is in request
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Make prediction
        result = inference.classify_audio(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            "success": True,
            "prediction": result
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Error processing audio: {str(e)}"
        }), 500


@app.route('/predict-url', methods=['POST'])
def predict_url():
    """Predict disease from audio URL."""
    
    if not model_loaded:
        return jsonify({
            "error": "Model not loaded. Please ensure cough_classifier.pt exists."
        }), 500
    
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400
    
    audio_url = data['url']
    
    try:
        import urllib.request
        
        # Download file
        filename = os.path.basename(audio_url).split('?')[0]
        if not filename:
            filename = "audio.wav"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        urllib.request.urlretrieve(audio_url, filepath)
        
        # Make prediction
        result = inference.classify_audio(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({
            "success": True,
            "prediction": result
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Error processing audio URL: {str(e)}"
        }), 500


@app.route('/top-predictions', methods=['POST'])
def get_top_predictions():
    """Get top-k predictions for uploaded audio file."""
    
    if not model_loaded:
        return jsonify({
            "error": "Model not loaded. Please ensure cough_classifier.pt exists."
        }), 500
    
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files['audio']
    top_k = request.form.get('top_k', 3, type=int)
    
    if not allowed_file(file.filename):
        return jsonify({
            "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        top_preds = inference.get_top_predictions(filepath, top_k=top_k)
        
        os.remove(filepath)
        
        return jsonify({
            "success": True,
            "top_predictions": [
                {
                    "disease": pred[0],
                    "confidence": float(pred[1])
                }
                for pred in top_preds
            ]
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Error processing audio: {str(e)}"
        }), 500


@app.route('/', methods=['GET'])
def index():
    """API documentation."""
    return jsonify({
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
    }), 200


if __name__ == '__main__':
    print("Starting Cough Classifier API...")
    print(f"Model loaded: {model_loaded}")
    print(f"Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
    print("\nAPI Documentation: http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)

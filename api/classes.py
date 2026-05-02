"""
Vercel Serverless API endpoint for /api/classes
Returns available disease classes
"""

import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from main import DISEASE_CLASSES
except Exception as e:
    DISEASE_CLASSES = {
        0: "Healthy",
        1: "Cold Cough",
        2: "COVID-19",
        3: "Asthma",
        4: "Bronchitis",
        5: "Tuberculosis",
        6: "Pneumonia",
    }


def handler(request):
    """Handle GET /api/classes requests"""
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "classes": DISEASE_CLASSES,
            "count": len(DISEASE_CLASSES)
        })
    }

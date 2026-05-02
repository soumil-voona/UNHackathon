FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for audio processing libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /app/api/requirements.txt

COPY backend /app/backend
COPY best_cough_classifier.pt /app/best_cough_classifier.pt

ENV PORT=10000
EXPOSE 10000

CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker backend.run:app --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120"]

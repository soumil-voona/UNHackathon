# CoughNet

CoughNet is a full-stack hackathon project for cough-based respiratory screening. The frontend lets a user record a short cough sample in the browser, shows the signal as it is captured, and sends the audio to a Python backend for classification. The backend returns a disease prediction with confidence scores and can fall back to a mock classifier if the trained model is not available, which keeps the demo runnable end to end.

## What it does

- Records cough audio directly from the browser with microphone access.
- Shows live recording state and a simple visual feedback loop while audio is captured.
- Sends the recording to a FastAPI service for analysis.
- Returns a ranked probability distribution across the supported respiratory classes.
- Flags the result as demo mode when the real model file is missing.
- Exposes utility API routes for health checks, class listing, and top-k predictions.

## Prerequisites

Before you start, make sure these are installed:

- Python 3.12 or newer
- Node.js 18 or newer
- Corepack, which ships with recent Node.js versions
- A browser with microphone access for the live demo

If `pnpm` is not installed globally, that is fine. This repo uses Corepack to run pnpm in a reproducible way.
If your Node.js install does not include Corepack yet, run `npm install -g corepack` once, then run `corepack enable`.

## Project layout

- `ReactFrontend/` contains the Vite frontend.
- `backend/` contains the FastAPI service, model code, and inference helpers.
- `documentation/` contains the longer project and dataset notes used during development.

## Supported classes

The API currently works with these labels:

- Healthy
- Cold Cough
- COVID-19
- Asthma
- Bronchitis
- Tuberculosis
- Pneumonia

## Fresh machine setup

If you are setting the project up on a new machine, use this flow.

### 1. Backend

1. Open a terminal in the repository root.
2. Create and activate a virtual environment with Python 3.12:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

3. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

4. Start the API server:

```bash
python api.py
```

The backend runs on `http://localhost:8000` by default. The API docs are available at `http://localhost:8000/docs`.

If `cough_classifier.pt` is present in `backend/`, the server uses the trained model. If it is missing, the API switches to mock inference so the demo still works.

### 2. Frontend

1. Open a second terminal.
2. Install the Node.js dependencies:

```bash
cd ReactFrontend
corepack enable
corepack pnpm install
```

3. Set the backend URL for the frontend:

```bash
echo 'VITE_API_URL=http://127.0.0.1:8000' > .env
```

4. Start the frontend dev server:

```bash
corepack pnpm dev
```

5. Open the local Vite URL shown in the terminal, usually `http://localhost:5173`.

If you want to point at a deployed backend later, change `VITE_API_URL` to that service URL.

## Run the backend

If you already created the backend virtual environment, you can restart the API with:

```bash
cd backend
source .venv/bin/activate
python api.py
```

## Run the frontend

If dependencies are already installed, restart the frontend with:

```bash
cd ReactFrontend
corepack pnpm dev
```

## Demo flow

1. Open the frontend in a browser.
2. Go to the live demo section.
3. Hold the record button and allow microphone access.
4. Speak or cough for about 3 seconds.
5. Release the button and wait for the prediction.
6. Review the probability breakdown and the mock-mode notice if the trained model is not loaded.

## API routes

- `GET /` returns a short API overview.
- `GET /health` reports backend status and whether the trained model loaded.
- `GET /classes` lists the supported disease labels.
- `POST /predict` uploads an audio file and returns a classification.
- `POST /predict-url` downloads audio from a URL and classifies it.
- `POST /top-predictions` returns the top-k likely classes.

## Notes

- The backend accepts common audio formats such as `wav`, `mp3`, `m4a`, `flac`, `webm`, and `ogg`.
- Uploaded files are cleaned up after each request.
- The frontend expects the backend to be running before you try the live demo.

## Built for the hackathon

CoughNet was built as a judge-friendly demo for accessible respiratory screening. The goal is to show the full path from microphone input to a machine-learning prediction in a way that is easy to run locally and easy to explain.

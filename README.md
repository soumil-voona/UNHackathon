# CoughNet — Respiratory Health Classification

CoughNet is a full-stack web application designed to analyze human cough recordings and classify potential respiratory conditions using machine learning. Built for the UN Hackathon, this project provides a seamless, browser-based intake module that captures audio, visualizes the signal in real-time, and processes it through a FastAPI backend.

## 🎯 Problem Statement

Respiratory diseases like Tuberculosis, COVID-19, and Pneumonia affect millions globally, often going undetected in early stages due to lack of accessible screening tools. Traditional diagnostic pathways require clinical visits and specialized equipment, creating a massive surveillance gap in low-resource settings.

## 💡 Solution

CoughNet bridges this gap by turning any commodity smartphone or laptop into a preliminary screening tool. By capturing a 3-second cough sample directly in the browser and analyzing its acoustic biomarkers (MFCCs and Mel-spectrograms), the system provides an immediate probability distribution across six respiratory conditions, enabling earlier triage and intervention.

## ✨ Features

- **Browser-Native Audio Capture**: Record cough samples directly from the web UI using the `MediaRecorder` API without requiring native app installation.
- **Real-Time Signal Visualization**: Live time-domain waveform and frequency-domain spectrogram rendering using the Web Audio API (`AnalyserNode`).
- **Mock AI Fallback Mode**: Fully functional demo mode that simulates realistic probability distributions when the trained PyTorch model is not present.
- **Dynamic Escalation Logic**: Automatically flags high-risk predictions (e.g., COVID-19, Tuberculosis, Pneumonia > 50% confidence) with clear clinical escalation warnings.
- **Local Asset Download**: Allows users to download their recorded `.webm` files for local inspection or dataset contribution.
- **Re-record Capability**: Seamlessly discard previous recordings and try again with a single click.

## 🧱 Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS + custom animations
- **Audio Processing**: Web Audio API, `MediaRecorder`
- **Visualization**: HTML5 Canvas, Three.js (Hero scene), GSAP (Scroll animations)
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Machine Learning**: PyTorch, Torchaudio
- **Audio Processing**: Librosa, Soundfile
- **File Handling**: `python-multipart` for robust audio uploads

---

## 📂 Project Structure

```text
UNHackathon/
├── ReactFrontend/               # React + Vite Frontend
│   ├── client/src/
│   │   ├── pages/Home.tsx       # Main UI, recording logic, and visualizations
│   │   ├── index.css            # Tailwind directives and custom styles
│   │   └── main.tsx             # React entry point
│   ├── package.json             # Frontend dependencies
│   └── .env.example             # Environment variables template
│
├── backend/                     # FastAPI Backend
│   ├── api.py                   # REST API endpoints and mock AI logic
│   ├── main.py                  # PyTorch CNN model architecture
│   ├── inference.py             # Model loading and prediction wrapper
│   ├── requirements.txt         # Python dependencies
│   └── uploads/                 # Temporary storage for audio processing
│
└── README.md                    # Project documentation
```

---

## 🚀 Setup Instructions

The project is designed to be fully runnable locally with minimal setup.

### 1. Start the Backend (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   python api.py
   ```
   *The server will start on `http://localhost:8000`. If `cough_classifier.pt` is not found, it will automatically fall back to the Mock AI mode so the app remains fully functional.*

### 2. Start the Frontend (React/Vite)

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd ReactFrontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   # or: pnpm install / yarn install
   ```
3. Create your environment file:
   ```bash
   cp .env.example .env
   ```
   *(Ensure `VITE_API_URL=http://127.0.0.1:8000` is set in the `.env` file)*
4. Start the development server:
   ```bash
   npm run dev
   # or: pnpm dev / yarn dev
   ```
5. Open your browser to the URL provided by Vite (usually `http://localhost:5173`).

---

## 🎤 Demo Instructions

1. Open the frontend application in your browser.
2. Scroll down to the **"Hear It for Yourself"** section.
3. Click and hold the **"Hold to Record"** button.
4. Allow microphone permissions if prompted by your browser.
5. Cough into your microphone for 3 seconds while holding the button.
6. Release the button. The audio will be sent to the backend.
7. Watch the probability distribution update with the classification results.
8. (Optional) Click **"Download Recording"** to save the audio file, or **"↺ Re-record"** to try again.

---

## 🧪 AI Processing Logic

The backend is architected to support both real inference and simulated demos:

1. **Real Inference**: If a trained PyTorch model (`cough_classifier.pt`) is placed in the `backend/` directory, `api.py` loads it via `inference.py`. It extracts a 64-bin Mel-spectrogram from the uploaded audio and runs it through a 4-layer Convolutional Neural Network to generate predictions.
2. **Mock AI Fallback**: If the model file is missing, the API gracefully falls back to a rule-based mock classifier. This ensures the frontend UI, loading states, and error handling can be fully evaluated by hackathon judges without requiring a heavy model download.

---

## 🌐 Deployment (Optional)

### Frontend (Vercel / Netlify)
1. Connect your GitHub repository to Vercel.
2. Set the Framework Preset to **Vite**.
3. Add the Environment Variable: `VITE_API_URL=https://your-backend-url.onrender.com`
4. Deploy.

### Backend (Render / Railway)
1. Create a new Web Service on Render connected to your repository.
2. Set the Root Directory to `backend`.
3. Set the Build Command to `pip install -r requirements.txt`.
4. Set the Start Command to `uvicorn api:app --host 0.0.0.0 --port $PORT`.
5. Deploy.

---

*Built for the UN Hackathon. Empowering global health through accessible acoustic screening.*

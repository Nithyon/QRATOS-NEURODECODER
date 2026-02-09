# QRATOS NeuroDecoder - Hackathon README

## Project
QRATOS NeuroDecoder is a hybrid quantum-inspired BCI (brain-computer interface) demo that streams EEG-like signals, applies Riemannian geometry features, and classifies intent with a quantum-inspired DAQC pipeline. The frontend visualizes live mission telemetry while the backend simulates or streams data over WebSockets.

## Hackathon Goal
Demonstrate real-time neural intent classification with a quantum-inspired pipeline and a mission HUD-style interface. Emphasis is on streaming, interpretability, and resilient fallback simulation.

## Features
- Real-time telemetry stream via WebSockets.
- Riemannian manifold feature extraction for EEG covariance.
- Quantum-inspired DAQC classifier using PennyLane.
- Live dashboard and backend source view.
- Automatic fallback to simulation when backend is offline.

## Tech Stack
- Frontend: React 19, TypeScript, Vite, Recharts, lucide-react
- Backend: FastAPI, Uvicorn, NumPy, SciPy, scikit-learn, PyRiemann, PennyLane

## Quick Start
### Frontend
1. From the repo root:
   - `cd qratos`
   - `npm install`
   - `npm run dev`
2. Open the dev server URL shown in the terminal.

### Backend
1. From the repo root:
   - `cd qratos/backend`
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - `uvicorn main:app --host 0.0.0.0 --port 8000`
2. The frontend will auto-connect to `ws://127.0.0.1:8000/ws/brain-stream`.

## Demo Flow
1. Start backend and frontend.
2. Open the dashboard tab to see live EEG metrics.
3. If backend is down, the UI switches to synthetic telemetry.
4. Use intent controls to simulate classification states.

## Repository Structure
- `qratos/` - frontend app
- `qratos/backend/` - FastAPI service, geometry, and quantum pipeline
- `qratos/components/` - UI components
- `qratos/services/` - WebSocket simulator client

## API Surface (Backend)
- `GET /` - health check
- `POST /upload` - upload EEG data
- `WS /ws/brain-stream` - live telemetry

## Team Notes
- Designed for live hackathon demos with graceful fallback.
- All data is either streamed from backend or simulated locally.

## Future Work
- Replace synthetic data with live EEG acquisition
- Expand DAQC classifier benchmarking
- Add model explainability overlays in the HUD

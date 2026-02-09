# QRATOS NeuroDecoder

Hybrid Riemannian-Quantum BCI pipeline for real-time neural intent classification.

Built by **Team Qratos** for **Quantathon 3.0**.

## Overview

| Layer | Tech | Purpose |
|-------|------|---------|
| Frontend | React 19 + Vite | Mission HUD dashboard |
| Backend | FastAPI + WebSockets | Real-time EEG streaming |
| Geometry | PyRiemann | Riemannian manifold feature extraction |
| Quantum | PennyLane (DAQC) | Quantum-inspired classification |

## Quick Start

```bash
# Frontend
cd qratos && npm install && npm run dev

# Backend (separate terminal)
cd qratos/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

See [HACKATHON.md](HACKATHON.md) for full demo instructions.

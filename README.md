# QRATOS NeuroDecoder

Hybrid Riemannian-Quantum BCI pipeline for real-time neural intent classification.

Built by **Team Qratos** for **Quantathon 3.0**.

## Overview

| Layer | Tech | Purpose |
|-------|------|---------|
| Frontend | React 19 + Vite | Mission HUD dashboard |
| Backend | FastAPI + WebSockets | Real-time EEG streaming |
| Geometry | PyRiemann | Riemannian manifold feature extraction |
| Quantum | PennyLane (DAQC) | Kipu-inspired quantum classification |

## 🚀 Quick Start (No Training Required!)

The system works immediately with random weights - perfect for demos:

```bash
# Backend (Terminal 1)
cd qratos/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd qratos
npm install
npm run dev
```

Open your browser to the URL shown (typically `http://localhost:5173`)

✨ **You'll see**: Live EEG visualization, quantum classification, and real-time metrics!

## 📚 Documentation

- **[Quick Start - No Training Required](QUICK_START_NO_TRAINING.md)** ⭐ Start here!
- **[Kipu Quantum Platform Guide](KIPU_PLATFORM_GUIDE.md)** - What is Kipu? Is it open source? How to access it?
- **[Quantum Platforms Comparison](QUANTUM_PLATFORMS_COMPARISON.md)** - Compare Kipu, IBM, AWS, Azure, Google & more
- **[FAQ - Frequently Asked Questions](FAQ.md)** - Common questions about training, Kipu, and usage
- **[HACKATHON.md](HACKATHON.md)** - Full demo instructions and training pipeline

## 🎓 About Kipu Quantum

**Kipu Quantum** is a commercial quantum computing platform specializing in **Digital-Analog Quantum Computing (DAQC)**. 

- ❌ **Not Open Source**: Commercial platform (contact Kipu Quantum for access)
- ✅ **This Repository**: Implements a Kipu-**inspired** DAQC approach using open-source PennyLane
- ✅ **No Kipu Account Needed**: Works standalone with PennyLane simulation

See [KIPU_PLATFORM_GUIDE.md](KIPU_PLATFORM_GUIDE.md) for details on accessing real Kipu hardware.

## 🎯 Pre-trained Models

### Option 1: Use Without Training (Instant)
The system works immediately with random weights - see [QUICK_START_NO_TRAINING.md](QUICK_START_NO_TRAINING.md)

### Option 2: Train Your Own Model (5-10 minutes)
```bash
cd qratos/backend
python generate_dataset.py  # Generate synthetic EEG
python prepare_data.py      # Extract Riemannian features
python train_daqc.py        # Train quantum classifier
```

Trained weights are saved to `data/daqc_weights.npz` and loaded automatically on next run.

### Option 3: Use Your Own EEG Data
Place your data as `qratos/backend/dataset.npy` (shape: `N×4×128`)
- Format: (Epochs, Channels, Time)
- Channels: C3, C4, Pz, Fz

See [QUICK_START_NO_TRAINING.md](QUICK_START_NO_TRAINING.md) for data format details.

# Quick Start Guide - No Training Required

This guide shows you how to run QRATOS NeuroDecoder **immediately** without any model training.

## 🚀 Instant Demo (2 minutes)

### Step 1: Install Dependencies

```bash
# Backend dependencies
cd qratos/backend
pip install -r requirements.txt

# Frontend dependencies  
cd ../
npm install
```

### Step 2: Start Backend (No Training Needed!)

```bash
cd qratos/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

**What you'll see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
[DAQC] Using random weights (untrained).
✅ Backend initialized successfully
```

✅ The system is now running with **random weights** - perfect for demos!

### Step 3: Start Frontend

Open a new terminal:

```bash
cd qratos
npm run dev
```

Visit: `http://localhost:5173` (or the URL shown)

### Step 4: Watch It Work! 

You'll immediately see:
- 🧠 **Live EEG Signals**: 4-channel visualization (C3, C4, Pz, Fz)
- 🎯 **Intent Classification**: Real-time predictions (Idle, Left Hand, Right Hand)
- 📊 **Metrics Dashboard**: 
  - Neural Activity
  - Riemannian Metric
  - Shannon Entropy
  - Quantum Compression Ratio
- ⚛️ **Quantum Circuit Stats**: See the Kipu DAQC in action

## 🎓 Understanding the Demo Mode

### What "Untrained" Means

When you see `[DAQC] Using random weights (untrained)`:
- ✅ System is fully functional
- ✅ Quantum circuit is working
- ✅ All visualization is real-time
- ⚠️ Predictions are random (not learned from data)

**This is perfect for:**
- Understanding the system architecture
- Testing the user interface
- Demonstrating quantum circuits
- Educational purposes
- Rapid prototyping

### Data Source: Synthetic EEG

The backend generates **scientifically accurate** Motor Imagery signals:
- **Mu waves** (10 Hz): Primary motor cortex activity
- **Beta waves** (20 Hz): Active thinking and attention
- **Gamma waves** (40 Hz): High-level information processing

The synthetic generator simulates **Event-Related Desynchronization (ERD)**:
- **Right Hand Intent**: Suppresses mu rhythm in C3 (left motor cortex)
- **Left Hand Intent**: Suppresses mu rhythm in C4 (right motor cortex)  
- **Idle State**: Balanced activity

## 📦 Option: Using Pre-trained Weights

If you want **accurate predictions**, train the model once (takes ~5-10 minutes):

```bash
cd qratos/backend

# Generate training data
python generate_dataset.py

# Extract Riemannian features  
python prepare_data.py

# Train quantum classifier
python train_daqc.py
```

**Output**: `data/daqc_weights.npz` (pre-trained model)

**Next time you run**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

You'll see:
```
[DAQC] ✅ Loaded trained weights from data/daqc_weights.npz
```

Now predictions are **trained** and accurate! 🎉

## 📁 Using Your Own EEG Data

Have real EEG data? Use it without training:

### Format Requirements

**File**: `qratos/backend/dataset.npy`  
**Shape**: `(N_samples, 4, 128)`
- `N_samples`: Number of epochs
- `4`: Channels (C3, C4, Pz, Fz)
- `128`: Time points per epoch

### Example: Convert CSV to NumPy

```python
import numpy as np
import pandas as pd

# Load your CSV
df = pd.read_csv('your_eeg_data.csv')

# Select 4 channels
channels = ['C3', 'C4', 'Pz', 'Fz']
data = df[channels].values  # Shape: (N_timepoints, 4)

# Epoch into 128-sample windows
n_epochs = len(data) // 128
data = data[:n_epochs * 128]  # Trim excess
epoched = data.reshape(n_epochs, 128, 4)  # (N, Time, Channels)

# Transpose to (N, Channels, Time)
final = epoched.transpose(0, 2, 1)

# Save
np.save('qratos/backend/dataset.npy', final)
print(f"Saved {final.shape}")
```

### Run with Your Data

```bash
cd qratos/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Log will show:
```
✅ Real Dataset Loaded Successfully. Shape: (N, 4, 128)
```

The frontend will display: **"Data Source: Real Dataset"**

## 🎮 Interactive Controls

The frontend includes live intent controls:

1. **Auto Mode** (default): Cycles through intents every 5 seconds
2. **Manual Mode**: Click intent buttons to simulate specific states:
   - Idle
   - Left Hand  
   - Right Hand

*Note*: Manual control only affects **synthetic data labeling**, not model predictions.

## 🔧 Advanced: Hot-Swapping Data

Upload new EEG data while the system is running:

### Using the API

```bash
curl -X POST http://127.0.0.1:8000/upload-dataset \
  -F "files=@session1.csv" \
  -F "files=@session2.csv"
```

The backend will:
1. Parse CSV files
2. Extract channels (C3, C4, Pz, Fz)
3. Epoch into 128-sample windows
4. Replace the current dataset **live**

No restart needed! ✨

## 🐛 Troubleshooting

### "ModuleNotFoundError: pennylane"

**Fix**:
```bash
cd qratos/backend
pip install -r requirements.txt
```

### "WebSocket connection failed"

**Fix**:
1. Ensure backend is running: `uvicorn main:app --port 8000`
2. Check port 8000 is not blocked
3. Try: `uvicorn main:app --host 0.0.0.0 --port 8000`

### "Data source: Synthetic" but I uploaded data

**Fix**:
1. Check file is named `dataset.npy` (not `.npz`)
2. Verify shape: `np.load('dataset.npy').shape` → `(N, 4, 128)`
3. Place in `qratos/backend/` directory
4. Restart backend

### Frontend shows "Backend Offline"

**Fix**:
1. Start backend first: `cd qratos/backend && uvicorn main:app --port 8000`
2. Wait for: `Uvicorn running on http://127.0.0.1:8000`
3. Then start frontend

## 📊 What to Expect (Untrained Mode)

### Prediction Behavior

With random weights, predictions will:
- ✅ Change over time (circuit is working)
- ✅ Show confidence scores (0-1 range)
- ⚠️ Not correlate with actual intents (not trained)
- ⚠️ Appear random (this is expected)

### Metrics Behavior  

All metrics are **real** and **accurate**:
- **Activity**: Mean absolute EEG amplitude ✅
- **Riemann Metric**: Geodesic distance on manifold ✅
- **Entropy**: Signal complexity (Shannon) ✅
- **Noise Level**: Standard deviation ✅
- **Compression Ratio**: DAQC vs standard gates ✅

Only the **intent classification** is untrained.

## 🎯 Next Steps

### For Demos
✅ You're ready! The system works great for demonstrations.

### For Accurate Predictions
Run the training pipeline once:
```bash
python generate_dataset.py  # 30 seconds
python prepare_data.py      # 1 minute  
python train_daqc.py        # 5-8 minutes
```

### For Research
1. Replace synthetic data with real EEG
2. Adjust Riemannian feature extraction in `geometry.py`
3. Tune quantum circuit hyperparameters in `quantum_engine.py`
4. Compare with classical baselines: `python train_baseline.py`

## 📚 Additional Resources

- **Full Documentation**: See `KIPU_PLATFORM_GUIDE.md`
- **Architecture Details**: See `HACKATHON.md`
- **Training Guide**: See `qratos/backend/train_daqc.py` comments
- **API Reference**: Visit `http://127.0.0.1:8000/docs` when backend is running

---

**🎉 That's it!** You're now running a hybrid quantum-classical BCI system with zero training required.

For questions, open an issue on GitHub or consult the team docs.

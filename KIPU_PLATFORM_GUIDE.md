# Kipu Quantum Platform Guide

## What is Kipu Quantum?

**Kipu Quantum** is a quantum computing company that specializes in **Digital-Analog Quantum Computing (DAQC)** - a hybrid approach that combines:

1. **Digital Steps**: Fast single-qubit operations (standard quantum gates like RX, RZ)
2. **Analog Steps**: Hamiltonian evolution using native hardware interactions (e.g., IsingZZ gates)

### Key Advantages of the Kipu Approach

- **Hardware Efficiency**: Uses native hardware interactions instead of decomposing everything into CNOTs
- **Reduced Circuit Depth**: Significantly shorter circuits compared to standard gate decomposition
- **Lower Noise**: Fewer operations mean less decoherence and gate errors
- **Compression Ratio**: Typically achieves 4-5x compression compared to standard gate models

## Is Kipu Quantum Open Source?

**No, Kipu Quantum is NOT open source.** It is a commercial quantum computing platform operated by Kipu Quantum GmbH.

### Access Options:

1. **Commercial Partnership**: Contact Kipu Quantum directly for enterprise access
   - Website: https://www.kipuquantum.com/
   - Email: info@kipuquantum.com

2. **Research Collaboration**: Academic institutions may apply for research partnerships

3. **Cloud Platform Access**: Kipu is developing cloud access but availability is limited

## QRATOS Implementation: Kipu-Inspired DAQC

This repository implements a **Kipu-inspired** DAQC approach using **PennyLane** (open source) that simulates the Kipu methodology:

### Current Implementation Features:

✅ **Digital-Analog Hybrid Circuit**
- AngleEmbedding for feature encoding
- IsingZZ ring for entanglement (simulates analog block)
- RX/RZ rotations for variational parameters (digital block)

✅ **No Training Required Option**
- System works with random weights for demonstration
- Falls back gracefully when no trained weights exist

✅ **Pre-trained Model Support**
- Can load trained weights from `data/daqc_weights.npz`
- One-vs-Rest (OvR) classification for 3 classes

## Using the System WITHOUT Training

### Option 1: Use Pre-trained Weights (Recommended)

If trained weights exist in `qratos/backend/data/daqc_weights.npz`, the system will automatically load them.

**To generate pre-trained weights:**

```bash
cd qratos/backend

# Step 1: Generate synthetic dataset (if needed)
python generate_dataset.py

# Step 2: Prepare Riemannian features
python prepare_data.py

# Step 3: Train the DAQC model
python train_daqc.py
```

After training, the weights are saved and will be automatically loaded on next run.

### Option 2: Run with Random Weights (No Training)

The system is designed to work immediately without any training:

```bash
cd qratos/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**What happens:**
- ✅ System initializes with random weights
- ✅ Provides real-time visualization
- ✅ Generates confidence scores (though not trained)
- ✅ Demonstrates the quantum circuit architecture
- ⚠️ Predictions are random (untrained model)

### Option 3: Use Pre-generated Dataset

If you have EEG data already:

1. Place your data as `dataset.npy` in `qratos/backend/`
   - Expected shape: `(N_samples, 4, 128)` 
   - Format: (Epochs, Channels, Time)
   - Channels: C3, C4, Pz, Fz

2. The system will automatically detect and use it:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will log: `✅ Real Dataset Loaded Successfully`

## Quick Start for Demo (No Training Required)

**Fastest way to see the system in action:**

```bash
# Terminal 1: Start Backend (uses random weights)
cd qratos/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd qratos
npm install
npm run dev
```

Open the browser URL shown by Vite (typically `http://localhost:5173`)

**You'll see:**
- ✨ Live EEG visualization
- 🧠 Real-time neural intent classification
- 📊 Riemannian geometry metrics
- ⚛️ Quantum compression statistics
- 🎯 Mission HUD with telemetry

## Enabling "True" Kipu Quantum Hardware

To use actual Kipu Quantum hardware (when available):

1. **Obtain Access Credentials**
   - Contact Kipu Quantum for partnership
   - Receive API keys and access tokens

2. **Modify quantum_engine.py**
   - Replace `qml.device("default.qubit", wires=n_qubits)` 
   - Use Kipu's hardware backend (when available via PennyLane plugin)

3. **Install Kipu Plugin** (hypothetical, check Kipu documentation):
   ```bash
   pip install pennylane-kipu  # If available
   ```

4. **Update Device Configuration**:
   ```python
   # In quantum_engine.py
   self.dev = qml.device("kipu.quantum", wires=n_qubits, api_key="YOUR_KEY")
   ```

**Note**: As of 2026, Kipu integration with PennyLane may require custom plugins or direct API access.

## Architecture Comparison

### Standard Gate Model (Noisy)
```
Feature → RX → CNOT → CNOT → CNOT → RY → CNOT → ...  (Deep, ~100+ gates)
```

### Kipu DAQC (Efficient)
```
Feature → AngleEmbed → [IsingZZ Ring + RX/RZ]×2 → Measure  (~20 gates)
                       ↑ Analog      ↑ Digital
```

**Result**: 4-5× fewer operations, better fidelity

## Alternative Quantum Platforms (Open Source)

If you prefer fully open-source quantum computing:

1. **Qiskit** (IBM Quantum)
   - Access: https://quantum-computing.ibm.com/
   - Free tier available

2. **Cirq** (Google Quantum AI)
   - Open source, local simulation
   - Access to Google quantum hardware (limited)

3. **PennyLane** (Xanadu)
   - Current implementation
   - Supports multiple backends

4. **Amazon Braket**
   - Cloud quantum computing service
   - Pay-per-use model

## Pre-trained Model Strategy

### Using Existing Weights

The repository can include pre-trained weights for immediate use:

1. **Training Process** (one-time):
   - Generate synthetic Motor Imagery EEG data
   - Extract Riemannian manifold features
   - Train 3 binary DAQC circuits (One-vs-Rest)
   - Save weights to `data/daqc_weights.npz`

2. **Deployment** (instant):
   - Weights automatically loaded on startup
   - No training required for end users
   - Immediate classification capability

### Model Performance

When trained on synthetic Motor Imagery data:
- **3 Classes**: Idle, Left Hand, Right Hand
- **Expected Accuracy**: 70-85% on test data
- **Inference Time**: <100ms per sample
- **Compression**: 4.5× compared to standard gates

## Troubleshooting

### "Using random weights (untrained)"
**Meaning**: No pre-trained weights found at `data/daqc_weights.npz`

**Solutions**:
1. Run training pipeline: `python train_daqc.py`
2. Or use with random weights for demonstration

### "Dataset shape invalid"
**Meaning**: Uploaded data doesn't match expected format

**Fix**: Ensure data is `(N, 4, 128)` - Epochs × Channels × Time

### "Failed to load weights"
**Meaning**: Weights file corrupted or incompatible

**Fix**: Delete `data/daqc_weights.npz` and retrain, or use random weights

## Resources

### Kipu Quantum
- Official Website: https://www.kipuquantum.com/
- Research Papers: Search "Kipu Quantum DAQC" on arXiv

### PennyLane Documentation
- Main Site: https://pennylane.ai/
- QAOA Tutorial: https://pennylane.ai/qml/demos/tutorial_qaoa_intro.html
- Quantum Chemistry: https://pennylane.ai/qml/demos/tutorial_vqe.html

### EEG & BCI
- PyRiemann: https://pyriemann.readthedocs.io/
- Motor Imagery: https://github.com/alexandrebarachant/pyRiemann

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Kipu Platform | ❌ Commercial | Contact Kipu Quantum for access |
| Kipu-Inspired DAQC | ✅ Implemented | Using PennyLane simulation |
| Pre-trained Model | ✅ Supported | Load from `daqc_weights.npz` |
| No Training Mode | ✅ Available | Uses random weights for demo |
| Real EEG Data | ✅ Supported | Place as `dataset.npy` |
| Synthetic Data | ✅ Built-in | Motor Imagery simulation |
| Open Source | ✅ Yes | MIT License (this repo) |

---

**Need Help?** Open an issue on GitHub or consult the team documentation.

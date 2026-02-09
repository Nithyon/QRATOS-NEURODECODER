# Frequently Asked Questions (FAQ)

## About Kipu Quantum

### Q: What is Kipu Quantum?
**A:** Kipu Quantum is a German quantum computing company specializing in Digital-Analog Quantum Computing (DAQC). They focus on hardware-efficient quantum algorithms that reduce circuit depth by using native hardware interactions.

### Q: Is Kipu Quantum open source?
**A:** No. Kipu Quantum is a **commercial platform**. To access their services:
- Visit: https://www.kipuquantum.com/
- Contact: info@kipuquantum.com
- Options: Enterprise partnerships, research collaborations

### Q: Do I need a Kipu account to use this repository?
**A:** No! This repository implements a **Kipu-inspired** approach using **open-source PennyLane**. It simulates the DAQC methodology without requiring access to Kipu's platform.

### Q: How do I enable "real" Kipu Quantum hardware?
**A:** 
1. Contact Kipu Quantum for API access credentials
2. Install any required Kipu plugin for PennyLane (if available)
3. Modify `quantum_engine.py` to use Kipu's device backend
4. See [KIPU_PLATFORM_GUIDE.md](KIPU_PLATFORM_GUIDE.md) for detailed instructions

### Q: What's the difference between this and "real" Kipu?
**A:** 

| Feature | This Repo (QRATOS) | Real Kipu Platform |
|---------|-------------------|-------------------|
| Cost | Free & Open Source | Commercial |
| Backend | PennyLane simulation | Real quantum hardware |
| Access | Immediate | Requires partnership |
| Accuracy | Software simulation | Hardware execution |
| Circuit Design | Kipu-inspired DAQC | Native Kipu compiler |

Both use the same **conceptual approach** (Digital-Analog blocks), but real Kipu runs on actual quantum processors.

## Training and Pre-trained Models

### Q: Can I use this without training a model?
**A:** **Yes!** The system works immediately with random weights:
```bash
cd qratos/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

You'll see: `[DAQC] Using random weights (untrained).`

This is perfect for:
- Demonstrations
- Understanding the architecture  
- UI testing
- Educational purposes

See [QUICK_START_NO_TRAINING.md](QUICK_START_NO_TRAINING.md) for details.

### Q: How do I get accurate predictions without training myself?
**A:** Two options:

**Option 1** - Train once (5-10 minutes):
```bash
cd qratos/backend
python generate_dataset.py  # Generate data
python prepare_data.py      # Extract features
python train_daqc.py        # Train model
```

**Option 2** - Use pre-trained weights (if provided):
- If this repository includes `qratos/backend/data/daqc_weights.npz`, the system loads it automatically
- No action needed - just start the backend

### Q: How long does training take?
**A:** On a modern laptop:
- Generate dataset: ~30 seconds
- Prepare features: ~1 minute
- Train DAQC: ~5-8 minutes (40 epochs, 3 binary classifiers)

**Total**: ~10 minutes one-time setup

### Q: Can I skip training and still get good results?
**A:** Not for accurate predictions. Options:
1. **Random weights**: System works but predictions are random
2. **Pre-trained weights**: Accurate (if provided in the repo)
3. **Train once**: 10 minutes for your own trained model

### Q: What accuracy can I expect after training?
**A:** On synthetic Motor Imagery data:
- **Idle class**: ~75-85%
- **Left Hand**: ~70-80%
- **Right Hand**: ~70-80%
- **Overall**: ~73-82% (3-class accuracy)

Performance depends on data quality and may vary with real EEG.

## Data and Datasets

### Q: Can I use my own EEG data?
**A:** Yes! Place your data as `qratos/backend/dataset.npy`:
- **Shape**: `(N_epochs, 4, 128)`
- **Channels**: C3, C4, Pz, Fz (motor cortex electrodes)
- **Format**: NumPy array

See [QUICK_START_NO_TRAINING.md](QUICK_START_NO_TRAINING.md) for conversion examples.

### Q: What if my data has different channels or sampling?
**A:** You'll need to preprocess:
1. **Resample** to 128 samples per epoch (or adjust `TIME_STEPS` in code)
2. **Select/interpolate** to get C3, C4, Pz, Fz channels
3. **Epoch** continuous data into trials

See `prepare_data.py` for reference.

### Q: What format is `dataset.npy`?
**A:**
```python
import numpy as np

data = np.load('dataset.npy')
print(data.shape)  # (N, 4, 128)

# N: Number of epochs/trials
# 4: Channels (C3, C4, Pz, Fz)  
# 128: Time points per epoch
```

### Q: Can I use CSV files?
**A:** Yes, via the upload API:
```bash
curl -X POST http://127.0.0.1:8000/upload-dataset \
  -F "files=@data.csv"
```

The backend will parse CSV and format automatically.

## Technical Questions

### Q: What is DAQC (Digital-Analog Quantum Computing)?
**A:** A hybrid approach that combines:
- **Digital blocks**: Standard quantum gates (RX, RZ) for variational parameters
- **Analog blocks**: Hamiltonian evolution (IsingZZ) for entanglement

**Advantage**: Uses hardware-native operations instead of decomposing to CNOTs, resulting in:
- Shorter circuits (4-5× compression)
- Lower noise (fewer gates)
- Better fidelity

### Q: What quantum backend does this use?
**A:** **PennyLane's `default.qubit`** - a high-performance quantum simulator.

To use other backends:
```python
# In quantum_engine.py
self.dev = qml.device("default.qubit", wires=n_qubits)

# Can change to:
# qml.device("qiskit.aer", wires=n_qubits)  # IBM simulator
# qml.device("cirq.simulator", wires=n_qubits)  # Google simulator  
# etc.
```

### Q: How many qubits does this use?
**A:** **4 qubits** - one per feature dimension after Riemannian projection.

This is sufficient for the 3-class Motor Imagery task.

### Q: Can I scale to more classes?
**A:** Yes! Modify:
1. `LABEL_MAP` in `quantum_engine.py`
2. Train additional OvR circuits in `train_daqc.py`
3. Update synthetic generator in `main.py`

The architecture supports any number of classes via One-vs-Rest.

### Q: What is Riemannian geometry doing here?
**A:** Transforms EEG covariance matrices to features:

1. **Covariance estimation**: Compute `C` for each epoch
2. **Manifold projection**: Map to tangent space at reference point
3. **Feature extraction**: Compact representation preserving geometry

**Why?** EEG covariance lives on a **Riemannian manifold** (symmetric positive-definite matrices). Standard Euclidean distance is wrong; geodesic distance is correct.

See `geometry.py` for implementation.

### Q: Why One-vs-Rest instead of multi-class?
**A:** Simplicity and modularity:
- Train 3 independent binary classifiers
- Each circuit: "Is this class X?" → Yes/No
- Final prediction: Class with highest confidence

**Alternative**: Single multi-class circuit with multiple output qubits (more complex).

## Installation and Setup

### Q: What are the system requirements?
**A:**
- **Python**: 3.8+ (3.9-3.11 recommended)
- **Node.js**: 18+
- **RAM**: 4GB+ (8GB recommended for training)
- **OS**: Linux, macOS, or Windows (WSL recommended)

### Q: Installation fails with "pennylane not found"
**A:**
```bash
cd qratos/backend
pip install -r requirements.txt
```

If still failing:
```bash
pip install pennylane pennylane-lightning --upgrade
```

### Q: Frontend shows "Backend Offline"
**A:** Check:
1. Backend is running: `uvicorn main:app --port 8000`
2. Port 8000 is not blocked
3. Both frontend and backend on same machine (or adjust WebSocket URL)

### Q: Training fails with "ModuleNotFoundError: pyriemann"
**A:**
```bash
pip install pyriemann scikit-learn scipy
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

## Performance and Optimization

### Q: Training is slow. How can I speed it up?
**A:** Several options:
1. **Reduce epochs**: Change `N_EPOCHS = 40` to `20` in `train_daqc.py`
2. **Increase batch size**: Change `BATCH_SIZE = 32` to `64`
3. **Use GPU**: Install `pennylane-lightning[gpu]`
4. **Reduce dataset size**: Train on fewer samples

### Q: Can I use GPU acceleration?
**A:** Yes! Install:
```bash
pip install pennylane-lightning-gpu
```

Then in `quantum_engine.py`:
```python
self.dev = qml.device("lightning.gpu", wires=n_qubits)
```

### Q: Real-time inference is laggy
**A:** Check:
1. **WebSocket delay**: Adjust `await asyncio.sleep(0.1)` in `main.py`
2. **Circuit caching**: PennyLane may compile circuits on first run
3. **CPU**: Quantum simulation is compute-intensive

### Q: How many predictions per second?
**A:** On typical hardware:
- **Untrained (random)**: ~10-20 Hz
- **Trained (OvR)**: ~5-10 Hz (3 circuits per prediction)
- **With caching**: ~15-30 Hz

## Comparison with Alternatives

### Q: How does this compare to classical ML?
**A:** See `train_baseline.py` for classical benchmarks:
- **SVM** (RBF kernel): ~75-80% accuracy
- **Random Forest**: ~72-78% accuracy
- **Logistic Regression**: ~68-75% accuracy

**DAQC performance**: Comparable (~73-82%), with quantum advantages in specific scenarios.

### Q: Why use quantum instead of classical?
**A:** Potential advantages:
1. **Expressivity**: Quantum circuits can represent complex functions efficiently
2. **Entanglement**: Captures feature correlations classically hard to model
3. **Future-proofing**: Scalable to quantum hardware when available
4. **Research**: Exploring quantum ML algorithms

**Current state**: Hybrid quantum-classical is competitive but not always superior on NISQ devices.

### Q: When should I use quantum ML?
**A:** Consider quantum when:
- ✅ You have access to quantum hardware
- ✅ Problem has inherent quantum structure
- ✅ Classical methods plateau
- ✅ Exploring cutting-edge research

**Not ideal when**:
- ❌ Pure classification task with no quantum advantage
- ❌ Large datasets (quantum memory is limited)
- ❌ Tight performance requirements (simulators are slow)

## Contributing and Support

### Q: Can I contribute to this project?
**A:** Yes! This is an open-source hackathon project. Contributions welcome:
- Bug fixes
- Performance improvements
- New quantum algorithms  
- Better visualizations
- Documentation

Open an issue or PR on GitHub.

### Q: Where can I get help?
**A:**
1. **Read docs**: Start with [QUICK_START_NO_TRAINING.md](QUICK_START_NO_TRAINING.md)
2. **Check issues**: Browse GitHub issues for similar problems
3. **Open an issue**: Describe your problem with error logs
4. **Team contact**: See repository maintainers

### Q: Is this production-ready?
**A:** No. This is a **hackathon prototype** for research and demonstration:
- ✅ Educational purposes
- ✅ Proof-of-concept
- ✅ Research experiments
- ❌ Production medical devices
- ❌ Critical systems
- ❌ Real patient data (without proper approval)

**Use responsibly** and with appropriate ethical oversight for any human subjects research.

### Q: What license is this under?
**A:** Check the LICENSE file in the repository. Typically MIT or similar permissive license for hackathon projects.

### Q: Can I use this for commercial purposes?
**A:** Depends on the license. Check:
1. **Repository LICENSE file**
2. **Dependencies' licenses** (PennyLane: Apache 2.0, PyRiemann: BSD, etc.)
3. **Kipu's IP**: If using their commercial platform

**Consult legal advice** for commercial deployment.

---

## Still Have Questions?

- 📖 **Read the docs**: [KIPU_PLATFORM_GUIDE.md](KIPU_PLATFORM_GUIDE.md), [QUICK_START_NO_TRAINING.md](QUICK_START_NO_TRAINING.md)
- 🐛 **Report bugs**: Open a GitHub issue
- 💬 **Discussion**: Check GitHub Discussions (if enabled)
- 📧 **Contact team**: See repository README for maintainer info

---

*Last updated: February 2026*

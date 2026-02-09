"""
Step 2: Train the Kipu DAQC quantum classifier on Riemannian features.

Strategy:
  - 3 classes (Idle=0, Left=1, Right=2)
  - One-vs-Rest: train 3 binary DAQC circuits, one per class
  - Each circuit: AngleEmbedding → (IsingZZ ring + RX/RZ) × layers → ⟨Z₀⟩
  - Loss: binary cross-entropy per circuit
  - Optimizer: PennyLane Adam

Output:
  - data/daqc_weights.npz       (trained weights for all 3 OvR circuits + coupling)
  - data/training_history.npz   (loss/accuracy curves)
  - Printed accuracy comparison with classical baselines
"""

import os
import sys
import time
import numpy as np

import pennylane as qml
from pennylane import numpy as pnp  # autograd-enabled numpy

# ─── Config ───────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FEATURES_PATH = os.path.join(DATA_DIR, "riemannian_features.npz")

N_QUBITS = 4
N_LAYERS = 2
COUPLING_STRENGTH = 1.5
LEARNING_RATE = 0.05
N_EPOCHS = 40
BATCH_SIZE = 32
SEED = 42

LABEL_MAP = {0: "Idle", 1: "Left Hand", 2: "Right Hand"}
N_CLASSES = len(LABEL_MAP)


# ─── DAQC Circuit Definition ─────────────────────────────────────────────────

dev = qml.device("default.qubit", wires=N_QUBITS)

@qml.qnode(dev, interface="autograd")
def daqc_circuit(features, weights, coupling):
    """
    Kipu DAQC circuit:
      1. AngleEmbedding (features → RX rotations)
      2. For each layer:
         a. Analog block: IsingZZ ring (simulates hardware-native entanglement)
         b. Digital block: RX + RZ per qubit (variational params)
      3. Measure ⟨Z₀⟩
    """
    qml.AngleEmbedding(features, wires=range(N_QUBITS), rotation='X')

    for layer in range(N_LAYERS):
        # Analog block — Ising ring
        for j in range(N_QUBITS - 1):
            qml.IsingZZ(coupling, wires=[j, j + 1])
        qml.IsingZZ(coupling, wires=[N_QUBITS - 1, 0])

        # Digital block — variational rotations
        for j in range(N_QUBITS):
            qml.RX(weights[layer, j, 0], wires=j)
            qml.RZ(weights[layer, j, 1], wires=j)

    return qml.expval(qml.PauliZ(0))


def circuit_output(features, weights, coupling):
    """Map raw ⟨Z₀⟩ ∈ [-1, 1] → probability ∈ (0, 1)."""
    raw = daqc_circuit(features, weights, coupling)
    return (raw + 1.0) / 2.0


# ─── Loss & Accuracy ─────────────────────────────────────────────────────────

def binary_cross_entropy(pred, target):
    """Numerically stable BCE."""
    eps = 1e-7
    pred = pnp.clip(pred, eps, 1 - eps)
    return -(target * pnp.log(pred) + (1 - target) * pnp.log(1 - pred))


def batch_loss(weights, coupling, X_batch, y_batch):
    """Average BCE over a mini-batch for one OvR circuit."""
    total = 0.0
    for i in range(len(X_batch)):
        features = prepare_features(X_batch[i])
        pred = circuit_output(features, weights, coupling)
        total = total + binary_cross_entropy(pred, y_batch[i])
    return total / len(X_batch)


def prepare_features(feature_vec):
    """Map a feature vector to n_qubits dimensions for AngleEmbedding."""
    # Take first N_QUBITS features (tangent space gives 10D for 4 channels)
    f = pnp.zeros(N_QUBITS)
    length = min(len(feature_vec), N_QUBITS)
    f[:length] = feature_vec[:length]
    # Normalize to [0, π]
    fmin, fmax = pnp.min(f), pnp.max(f)
    if fmax - fmin > 1e-8:
        f = (f - fmin) / (fmax - fmin) * np.pi
    return f


# ─── Training ────────────────────────────────────────────────────────────────

def train_one_vs_rest(class_idx, F_train, y_train, F_val, y_val):
    """
    Train one binary DAQC circuit for class `class_idx` vs all others.
    Returns trained weights, coupling, and history dict.
    """
    print(f"\n{'═' * 60}")
    print(f"  Training OvR circuit: class {class_idx} = '{LABEL_MAP[class_idx]}'")
    print(f"{'═' * 60}")

    # Binary labels: 1 if this class, 0 otherwise
    y_train_bin = (y_train == class_idx).astype(np.float64)
    y_val_bin = (y_val == class_idx).astype(np.float64)

    # Init trainable params (PennyLane autograd tensors)
    pnp.random.seed(SEED + class_idx)
    weights = pnp.array(
        pnp.random.uniform(0, 2 * np.pi, (N_LAYERS, N_QUBITS, 2)),
        requires_grad=True
    )
    coupling = pnp.array(COUPLING_STRENGTH, requires_grad=True)

    opt = qml.AdamOptimizer(stepsize=LEARNING_RATE)

    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    n_train = len(F_train)

    for epoch in range(1, N_EPOCHS + 1):
        t0 = time.time()

        # Shuffle
        perm = np.random.permutation(n_train)
        F_shuffled = F_train[perm]
        y_shuffled = y_train_bin[perm]

        # Mini-batch gradient descent
        epoch_loss = 0.0
        n_batches = 0
        for start in range(0, n_train, BATCH_SIZE):
            end = min(start + BATCH_SIZE, n_train)
            X_b = pnp.array(F_shuffled[start:end], requires_grad=False)
            y_b = pnp.array(y_shuffled[start:end], requires_grad=False)

            (weights, coupling), loss_val = opt.step_and_cost(
                batch_loss, weights, coupling, X_b, y_b
            )
            epoch_loss += float(loss_val)
            n_batches += 1

        avg_train_loss = epoch_loss / n_batches

        # Validation loss + accuracy
        val_preds = []
        val_loss = 0.0
        for i in range(len(F_val)):
            features = prepare_features(F_val[i])
            pred = float(circuit_output(features, weights, coupling))
            val_preds.append(pred)
            val_loss += float(binary_cross_entropy(
                pnp.array(pred), pnp.array(y_val_bin[i])
            ))
        val_loss /= len(F_val)

        val_preds_bin = (np.array(val_preds) > 0.5).astype(int)
        val_acc = np.mean(val_preds_bin == y_val_bin)

        # Train accuracy (quick estimate on first 200 samples)
        train_preds = []
        for i in range(min(200, n_train)):
            features = prepare_features(F_train[i])
            pred = float(circuit_output(features, weights, coupling))
            train_preds.append(pred)
        train_preds_bin = (np.array(train_preds) > 0.5).astype(int)
        train_acc = np.mean(train_preds_bin == y_train_bin[:len(train_preds)])

        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(float(train_acc))
        history["val_acc"].append(float(val_acc))

        elapsed = time.time() - t0
        if epoch % 5 == 0 or epoch == 1:
            print(
                f"  Epoch {epoch:3d}/{N_EPOCHS}  "
                f"loss={avg_train_loss:.4f}  val_loss={val_loss:.4f}  "
                f"val_acc={val_acc:.4f}  ({elapsed:.1f}s)"
            )

    return weights, coupling, history


# ─── Evaluation ───────────────────────────────────────────────────────────────

def evaluate_ovr(all_weights, all_couplings, F_test, y_test):
    """Run all 3 OvR circuits and pick argmax as the predicted class."""
    n = len(F_test)
    scores = np.zeros((n, N_CLASSES))

    for cls in range(N_CLASSES):
        for i in range(n):
            features = prepare_features(F_test[i])
            scores[i, cls] = float(circuit_output(
                features, all_weights[cls], all_couplings[cls]
            ))

    preds = np.argmax(scores, axis=1)
    acc = np.mean(preds == y_test)

    print(f"\n{'═' * 60}")
    print(f"  DAQC Test Accuracy (OvR, 3-class): {acc:.4f}")
    print(f"{'═' * 60}")

    # Per-class breakdown
    for cls in range(N_CLASSES):
        mask = y_test == cls
        cls_acc = np.mean(preds[mask] == y_test[mask]) if mask.sum() > 0 else 0
        print(f"  {LABEL_MAP[cls]:>12s}: {cls_acc:.4f}  ({mask.sum()} samples)")

    return acc, preds


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(FEATURES_PATH):
        print(f"❌ Features not found at {FEATURES_PATH}")
        print("   Run  python train_baseline.py  first.")
        sys.exit(1)

    print(f"Loading Riemannian features from {FEATURES_PATH}...")
    data = np.load(FEATURES_PATH)
    F_train, y_train = data['F_train'], data['y_train']
    F_val, y_val = data['F_val'], data['y_val']
    F_test, y_test = data['F_test'], data['y_test']
    print(f"  Train: {F_train.shape}  Val: {F_val.shape}  Test: {F_test.shape}")

    # Train one circuit per class (One-vs-Rest)
    all_weights = []
    all_couplings = []
    all_histories = {}

    for cls in range(N_CLASSES):
        weights, coupling, history = train_one_vs_rest(
            cls, F_train, y_train, F_val, y_val
        )
        all_weights.append(np.array(weights))
        all_couplings.append(float(coupling))
        all_histories[f"class_{cls}"] = history

    # Evaluate
    acc, preds = evaluate_ovr(all_weights, all_couplings, F_test, y_test)

    # Save trained weights
    weights_path = os.path.join(DATA_DIR, "daqc_weights.npz")
    save_dict = {
        "n_qubits": N_QUBITS,
        "n_layers": N_LAYERS,
        "couplings": np.array(all_couplings),
    }
    for cls in range(N_CLASSES):
        save_dict[f"weights_class_{cls}"] = all_weights[cls]

    np.savez(weights_path, **save_dict)
    print(f"\n✅ Trained DAQC weights saved to {weights_path}")

    # Save training history
    history_path = os.path.join(DATA_DIR, "training_history.npz")
    history_save = {}
    for cls in range(N_CLASSES):
        for key, vals in all_histories[f"class_{cls}"].items():
            history_save[f"class_{cls}_{key}"] = np.array(vals)
    np.savez(history_path, **history_save)
    print(f"✅ Training history saved to {history_path}")

    print(f"\n🎯 DAQC training complete!  Test accuracy: {acc:.4f}")
    print(f"   Next: restart main.py — it will auto-load trained weights.")


if __name__ == "__main__":
    main()

"""
Step 0: Generate a labeled synthetic EEG dataset for training.

Reuses the same ERD (Event-Related Desynchronization) physics from main.py
so that the trained model is consistent with the live simulation.

Output:
  - data/synthetic_dataset.npz  (X_train, y_train, X_val, y_val, X_test, y_test)
  - Each epoch: (4 channels, 128 timesteps)
  - Labels:  0 = Idle, 1 = Left Hand, 2 = Right Hand
"""

import os
import numpy as np

# ─── Config ───────────────────────────────────────────────────────────────────
EPOCHS_PER_CLASS = 1000       # total epochs per intent class
CHANNELS = 4                  # C3, C4, Pz, Fz
TIME_POINTS = 128             # ~1 s at 128 Hz
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15
SEED = 42
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")

INTENTS = ["Idle", "Left Hand", "Right Hand"]


# ─── Synthetic EEG Generator (same physics as main.py) ───────────────────────

def generate_epoch(intent: str, step: int) -> np.ndarray:
    """
    Generate one EEG epoch of shape (4, 128).
    Uses contralateral ERD model:
      - Idle:       high Mu on both C3/C4
      - Right Hand: C3 desynchronized (left motor cortex → right hand)
      - Left Hand:  C4 desynchronized (right motor cortex → left hand)
    """
    t = np.linspace(0, 1, TIME_POINTS) + (step * 0.1)

    # Base rhythms
    mu_wave = np.sin(2 * np.pi * 10 * t)       # Mu  ~10 Hz
    beta_wave = np.sin(2 * np.pi * 20 * t)     # Beta ~20 Hz
    gamma_wave = 0.3 * np.sin(2 * np.pi * 40 * t)  # Gamma ~40 Hz

    # Amplitudes per intent (ERD = suppression)
    amp_c3, amp_c4 = 1.0, 1.0
    if intent == "Right Hand":
        amp_c3 = 0.2   # left cortex desynchronizes
    elif intent == "Left Hand":
        amp_c4 = 0.2   # right cortex desynchronizes

    # Channel construction with realistic noise
    c3 = (mu_wave * amp_c3) + (beta_wave * 0.5) + np.random.normal(0, 0.3, TIME_POINTS)
    c4 = (mu_wave * amp_c4) + (beta_wave * 0.5) + np.random.normal(0, 0.3, TIME_POINTS)
    pz = (mu_wave * 1.2) + np.random.normal(0, 0.4, TIME_POINTS)
    fz = (beta_wave * 0.8) + gamma_wave + np.random.normal(0, 0.5, TIME_POINTS)

    return np.stack([c3, c4, pz, fz])  # (4, 128)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    np.random.seed(SEED)

    all_epochs = []
    all_labels = []

    for label_idx, intent in enumerate(INTENTS):
        print(f"Generating {EPOCHS_PER_CLASS} epochs for '{intent}' (label={label_idx})...")
        for step in range(EPOCHS_PER_CLASS):
            epoch = generate_epoch(intent, step)
            all_epochs.append(epoch)
            all_labels.append(label_idx)

    X = np.array(all_epochs, dtype=np.float32)   # (3000, 4, 128)
    y = np.array(all_labels, dtype=np.int64)      # (3000,)

    # Shuffle
    indices = np.random.permutation(len(X))
    X, y = X[indices], y[indices]

    # Split
    n = len(X)
    n_train = int(n * TRAIN_RATIO)
    n_val = int(n * VAL_RATIO)

    X_train, y_train = X[:n_train], y[:n_train]
    X_val, y_val = X[n_train:n_train + n_val], y[n_train:n_train + n_val]
    X_test, y_test = X[n_train + n_val:], y[n_train + n_val:]

    print(f"\nSplit sizes:")
    print(f"  Train: {X_train.shape[0]}  Val: {X_val.shape[0]}  Test: {X_test.shape[0]}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "synthetic_dataset.npz")
    np.savez(
        out_path,
        X_train=X_train, y_train=y_train,
        X_val=X_val, y_val=y_val,
        X_test=X_test, y_test=y_test,
    )
    print(f"\n✅ Saved to {out_path}")
    print(f"   X shape: (epochs, {CHANNELS}, {TIME_POINTS})  |  Labels: {dict(zip(range(3), INTENTS))}")


if __name__ == "__main__":
    main()

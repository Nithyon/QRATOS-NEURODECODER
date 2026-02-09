"""
Step 1: Train a classical baseline on Riemannian features.

Pipeline:
  1. Load synthetic_dataset.npz  (epochs of shape (N, 4, 128))
  2. Compute covariance matrices → tangent-space features via PyRiemann
  3. StandardScaler → Logistic Regression & Linear SVM
  4. Report accuracy on train / val / test
  5. Save fitted scaler + features as .npz for the quantum training step

Output:
  - data/riemannian_features.npz   (tangent-space vectors + labels, split)
  - data/scaler.joblib              (fitted StandardScaler)
  - Printed accuracy table
"""

import os
import sys
import numpy as np
import joblib

from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

# ─── Config ───────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATASET_PATH = os.path.join(DATA_DIR, "synthetic_dataset.npz")
LABEL_MAP = {0: "Idle", 1: "Left Hand", 2: "Right Hand"}


# ─── Riemannian Feature Extraction ───────────────────────────────────────────

def extract_riemannian_features(X_train, X_val, X_test):
    """
    X: (N, 4, 128)  →  features: (N, 10)   [4*(4+1)/2 = 10 tangent-space dims]
    """
    print("Computing covariance matrices (LWF estimator)...")
    cov_est = Covariances(estimator='lwf')

    cov_train = cov_est.transform(X_train)
    cov_val = cov_est.transform(X_val)
    cov_test = cov_est.transform(X_test)

    print("Projecting to tangent space (Riemannian metric)...")
    ts = TangentSpace(metric='riemann')
    F_train = ts.fit_transform(cov_train)
    F_val = ts.transform(cov_val)
    F_test = ts.transform(cov_test)

    print(f"Feature shape: {F_train.shape[1]}D per epoch")
    return F_train, F_val, F_test


# ─── Classical Baselines ──────────────────────────────────────────────────────

def train_baselines(F_train, y_train, F_val, y_val, F_test, y_test):
    """Train LogReg + SVM and print results."""

    scaler = StandardScaler()
    F_train_s = scaler.fit_transform(F_train)
    F_val_s = scaler.transform(F_val)
    F_test_s = scaler.transform(F_test)

    results = {}

    for name, clf in [
        ("LogisticRegression", LogisticRegression(max_iter=1000, multi_class='multinomial')),
        ("LinearSVM", LinearSVC(max_iter=2000, dual=False)),
    ]:
        clf.fit(F_train_s, y_train)
        acc_train = accuracy_score(y_train, clf.predict(F_train_s))
        acc_val = accuracy_score(y_val, clf.predict(F_val_s))
        acc_test = accuracy_score(y_test, clf.predict(F_test_s))

        results[name] = {"train": acc_train, "val": acc_val, "test": acc_test}

        print(f"\n{'=' * 50}")
        print(f"  {name}")
        print(f"{'=' * 50}")
        print(f"  Train acc: {acc_train:.4f}")
        print(f"  Val acc:   {acc_val:.4f}")
        print(f"  Test acc:  {acc_test:.4f}")
        print(f"\n  Classification Report (test):")
        print(classification_report(
            y_test, clf.predict(F_test_s),
            target_names=list(LABEL_MAP.values())
        ))

    return scaler, F_train_s, F_val_s, F_test_s


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Dataset not found at {DATASET_PATH}")
        print("   Run  python generate_dataset.py  first.")
        sys.exit(1)

    print(f"Loading dataset from {DATASET_PATH}...")
    data = np.load(DATASET_PATH)
    X_train, y_train = data['X_train'], data['y_train']
    X_val, y_val = data['X_val'], data['y_val']
    X_test, y_test = data['X_test'], data['y_test']

    print(f"  Train: {X_train.shape}  Val: {X_val.shape}  Test: {X_test.shape}")

    # Extract Riemannian features
    F_train, F_val, F_test = extract_riemannian_features(X_train, X_val, X_test)

    # Train classical baselines & fit scaler
    scaler, F_train_s, F_val_s, F_test_s = train_baselines(
        F_train, y_train, F_val, y_val, F_test, y_test
    )

    # Save features + scaler for the DAQC training step
    features_path = os.path.join(DATA_DIR, "riemannian_features.npz")
    np.savez(
        features_path,
        F_train=F_train_s, y_train=y_train,
        F_val=F_val_s, y_val=y_val,
        F_test=F_test_s, y_test=y_test,
    )
    print(f"\n✅ Scaled features saved to {features_path}")

    scaler_path = os.path.join(DATA_DIR, "scaler.joblib")
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler saved to {scaler_path}")

    print("\n🎯 Classical baseline done. Next: python train_daqc.py")


if __name__ == "__main__":
    main()

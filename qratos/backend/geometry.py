import numpy as np
from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace

class RiemannianManifold:
    """
    Handles the Riemannian Geometry transformations for EEG data.
    Maps SPD (Symmetric Positive Definite) Covariance Matrices to the Euclidean Tangent Space.
    
    Why Riemannian?
    EEG covariance matrices live on a curved manifold (SPD). Euclidean math (like standard deep learning)
    distorts distances on this manifold. Mapping to Tangent Space flattens the local geometry,
    making signal separation much easier for the Quantum Classifier.
    """
    def __init__(self):
        # LWF (Ledoit-Wolf) estimator is robust for high-dimensional noisy data (like EEG)
        self.cov_estimator = Covariances(estimator='lwf')
        # Map to tangent space at the geometric mean (Riemannian metric)
        self.tangent_space = TangentSpace(metric='riemann')

    def transform(self, X):
        """
        Args:
            X: EEG epochs of shape (N_epochs, N_channels, N_times)
        Returns:
            Tangent vectors of shape (N_epochs, N_features)
        """
        # 1. Map to SPD Manifold (Covariance Matrices)
        # Shape: (N_epochs, N_channels, N_channels)
        cov_matrices = self.cov_estimator.transform(X)
        
        # 2. Project to Tangent Space (Euclidean Vector Space)
        # This flattens the curved manifold while preserving geodesic distances locally.
        # Shape: (N_epochs, N_channels * (N_channels + 1) / 2)
        tangent_vectors = self.tangent_space.fit_transform(cov_matrices)
        
        return tangent_vectors

    def compute_riemannian_metric(self, cov_matrix):
        """
        Computes a scalar metric representing signal complexity/energy 
        on the manifold (Trace/Frobenius Norm).
        Used for the 'Riemannian Metric' HUD gauge.
        """
        return np.trace(cov_matrix)
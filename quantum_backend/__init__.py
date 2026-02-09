"""
Quantum Backend for QRATOS-NEURODECODER
Integrates Kipu Quantum-inspired algorithms with EEG analysis
"""

__version__ = "0.1.0"
__author__ = "QRATOS Team"

from .circuits import QuantumCircuitBuilder, QuantumEEGProcessor
from .eeg_processing import EEGDataPreprocessor, QuantumFeatureExtractor
from .api import QuantumAPI

__all__ = [
    'QuantumCircuitBuilder',
    'QuantumEEGProcessor',
    'EEGDataPreprocessor',
    'QuantumFeatureExtractor',
    'QuantumAPI'
]

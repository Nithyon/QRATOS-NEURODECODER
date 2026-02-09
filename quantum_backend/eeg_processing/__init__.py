"""
EEG Data Preprocessing and Quantum Feature Extraction
"""

import numpy as np
from typing import List, Tuple, Optional, Dict


class EEGDataPreprocessor:
    """
    Preprocess EEG data for quantum processing
    Handles filtering, normalization, and segmentation
    """
    
    def __init__(self, sampling_rate: float = 256.0):
        """
        Initialize EEG preprocessor
        
        Args:
            sampling_rate: Sampling rate of EEG data in Hz
        """
        self.sampling_rate = sampling_rate
        self.frequency_bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 50)
        }
    
    def normalize(self, data: np.ndarray) -> np.ndarray:
        """
        Normalize EEG data to [0, 1] range
        
        Args:
            data: Raw EEG data
        
        Returns:
            Normalized data
        """
        data_min = np.min(data)
        data_max = np.max(data)
        
        if data_max - data_min == 0:
            return np.zeros_like(data)
        
        return (data - data_min) / (data_max - data_min)
    
    def segment_signal(self, data: np.ndarray, window_size: float = 2.0, 
                       overlap: float = 0.5) -> List[np.ndarray]:
        """
        Segment EEG signal into windows
        
        Args:
            data: EEG signal
            window_size: Window size in seconds
            overlap: Overlap ratio (0 to 1)
        
        Returns:
            List of signal segments
        """
        window_samples = int(window_size * self.sampling_rate)
        step_samples = int(window_samples * (1 - overlap))
        
        segments = []
        for i in range(0, len(data) - window_samples + 1, step_samples):
            segment = data[i:i + window_samples]
            segments.append(segment)
        
        return segments
    
    def extract_band_power(self, signal: np.ndarray, band: Tuple[float, float]) -> float:
        """
        Extract power in a specific frequency band
        
        Args:
            signal: EEG signal
            band: Frequency band (low, high) in Hz
        
        Returns:
            Power in the band
        """
        # Simple FFT-based power estimation
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/self.sampling_rate)
        
        # Find indices for the band
        band_idx = np.where((freqs >= band[0]) & (freqs <= band[1]))[0]
        
        # Calculate power
        power = np.sum(np.abs(fft[band_idx]) ** 2)
        
        return power
    
    def extract_classical_features(self, signal: np.ndarray) -> Dict[str, float]:
        """
        Extract classical features from EEG signal
        
        Args:
            signal: EEG signal segment
        
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Statistical features
        features['mean'] = np.mean(signal)
        features['std'] = np.std(signal)
        features['variance'] = np.var(signal)
        features['min'] = np.min(signal)
        features['max'] = np.max(signal)
        
        # Frequency band powers
        for band_name, band_range in self.frequency_bands.items():
            features[f'power_{band_name}'] = self.extract_band_power(signal, band_range)
        
        return features


class QuantumFeatureExtractor:
    """
    Extract quantum-enhanced features from EEG data
    Bridges classical preprocessing and quantum processing
    """
    
    def __init__(self, num_features: int = 8):
        """
        Initialize quantum feature extractor
        
        Args:
            num_features: Number of features to extract
        """
        self.num_features = num_features
        self.preprocessor = EEGDataPreprocessor()
    
    def prepare_for_quantum(self, signal: np.ndarray) -> np.ndarray:
        """
        Prepare EEG signal for quantum processing
        
        Args:
            signal: Raw EEG signal
        
        Returns:
            Quantum-ready feature vector
        """
        # Extract classical features
        features_dict = self.preprocessor.extract_classical_features(signal)
        
        # Select most relevant features
        selected_features = [
            features_dict['mean'],
            features_dict['std'],
            features_dict['power_delta'],
            features_dict['power_theta'],
            features_dict['power_alpha'],
            features_dict['power_beta'],
            features_dict['power_gamma'],
            features_dict['variance']
        ]
        
        # Normalize for quantum encoding
        features = np.array(selected_features[:self.num_features])
        normalized_features = self.preprocessor.normalize(features)
        
        return normalized_features
    
    def quantum_amplitude_encoding(self, features: np.ndarray) -> np.ndarray:
        """
        Encode features using amplitude encoding
        Prepares features for quantum state preparation
        
        Args:
            features: Classical features
        
        Returns:
            Amplitude-encoded features
        """
        # Ensure features are normalized
        norm = np.linalg.norm(features)
        if norm > 0:
            return features / norm
        return features
    
    def hybrid_feature_vector(self, signal: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Create hybrid classical-quantum feature vector
        
        Args:
            signal: EEG signal
        
        Returns:
            Dictionary with classical and quantum-ready features
        """
        # Classical features
        classical_features = self.preprocessor.extract_classical_features(signal)
        
        # Quantum-ready features
        quantum_features = self.prepare_for_quantum(signal)
        
        # Amplitude encoded features
        amplitude_encoded = self.quantum_amplitude_encoding(quantum_features)
        
        return {
            'classical': np.array(list(classical_features.values())),
            'quantum_ready': quantum_features,
            'amplitude_encoded': amplitude_encoded
        }


def demo_eeg_processing():
    """
    Demonstration of EEG processing pipeline
    """
    print("=" * 60)
    print("QRATOS-NEURODECODER: EEG Processing Demo")
    print("Classical-Quantum Hybrid Pipeline")
    print("=" * 60)
    
    # Generate synthetic EEG data
    sampling_rate = 256
    duration = 10  # seconds
    t = np.linspace(0, duration, int(sampling_rate * duration))
    
    # Simulate EEG with multiple frequency components
    eeg_signal = (
        0.5 * np.sin(2 * np.pi * 1.5 * t) +   # Delta
        0.3 * np.sin(2 * np.pi * 6 * t) +     # Theta
        0.4 * np.sin(2 * np.pi * 10 * t) +    # Alpha
        0.2 * np.sin(2 * np.pi * 20 * t) +    # Beta
        0.1 * np.random.randn(len(t))         # Noise
    )
    
    print(f"\n✓ Generated synthetic EEG signal")
    print(f"  Duration: {duration}s, Sampling rate: {sampling_rate}Hz")
    print(f"  Total samples: {len(eeg_signal)}")
    
    # Initialize processors
    preprocessor = EEGDataPreprocessor(sampling_rate=sampling_rate)
    quantum_extractor = QuantumFeatureExtractor(num_features=8)
    
    # Segment signal
    print("\n→ Segmenting signal...")
    segments = preprocessor.segment_signal(eeg_signal, window_size=2.0, overlap=0.5)
    print(f"✓ Created {len(segments)} segments")
    
    # Process first segment
    segment = segments[0]
    print(f"\n→ Processing segment 1 (length: {len(segment)} samples)")
    
    # Extract classical features
    classical_features = preprocessor.extract_classical_features(segment)
    print(f"✓ Extracted {len(classical_features)} classical features")
    print("  Sample features:")
    for name, value in list(classical_features.items())[:5]:
        print(f"    {name}: {value:.4f}")
    
    # Prepare for quantum processing
    print("\n→ Preparing quantum features...")
    hybrid_features = quantum_extractor.hybrid_feature_vector(segment)
    print(f"✓ Classical features: {hybrid_features['classical'].shape}")
    print(f"✓ Quantum-ready features: {hybrid_features['quantum_ready'].shape}")
    print(f"✓ Amplitude-encoded: {hybrid_features['amplitude_encoded'].shape}")
    
    print("\n  Quantum-ready feature vector:")
    print(f"    {hybrid_features['quantum_ready']}")
    
    print("\n" + "=" * 60)
    print("EEG Processing pipeline completed successfully!")
    print("Ready for quantum circuit processing")
    print("=" * 60)


if __name__ == "__main__":
    demo_eeg_processing()

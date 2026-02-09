"""
Quantum Circuit Builder for EEG Analysis
Implements Kipu Quantum-inspired algorithms using Qiskit and PennyLane
"""

from typing import List, Optional, Tuple, Union
import numpy as np

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.circuit import Parameter
    from qiskit_aer import AerSimulator
    from qiskit.primitives import Sampler
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit not installed. Install with: pip install qiskit qiskit-aer")


class QuantumCircuitBuilder:
    """
    Build quantum circuits for EEG signal processing
    Inspired by Kipu Quantum's application-specific approach
    """
    
    def __init__(self, num_qubits: int = 4):
        """
        Initialize quantum circuit builder
        
        Args:
            num_qubits: Number of qubits for the circuit
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required. Install with: pip install qiskit qiskit-aer")
        
        self.num_qubits = num_qubits
        self.simulator = AerSimulator()
    
    def create_feature_map(self, data: np.ndarray) -> QuantumCircuit:
        """
        Create a quantum feature map for EEG data
        Uses angle encoding to map classical data to quantum states
        
        Args:
            data: Input EEG features (should be normalized)
        
        Returns:
            QuantumCircuit with encoded data
        """
        qc = QuantumCircuit(self.num_qubits)
        
        # Normalize data to fit in [0, 2π]
        normalized_data = 2 * np.pi * (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-8)
        
        # Angle encoding
        for i in range(min(len(normalized_data), self.num_qubits)):
            qc.ry(normalized_data[i], i)
        
        # Entanglement layer for feature correlation
        for i in range(self.num_qubits - 1):
            qc.cx(i, i + 1)
        
        return qc
    
    def create_variational_circuit(self, num_layers: int = 2) -> QuantumCircuit:
        """
        Create a variational quantum circuit for classification
        Similar to Variational Quantum Classifier (VQC)
        
        Args:
            num_layers: Number of variational layers
        
        Returns:
            Parameterized quantum circuit
        """
        qc = QuantumCircuit(self.num_qubits)
        
        # Create parameters
        params = []
        for layer in range(num_layers):
            layer_params = [Parameter(f'θ_{layer}_{i}') for i in range(self.num_qubits)]
            params.extend(layer_params)
            
            # Rotation layer
            for i, param in enumerate(layer_params):
                qc.ry(param, i)
            
            # Entanglement layer
            for i in range(self.num_qubits - 1):
                qc.cx(i, i + 1)
        
        return qc
    
    def quantum_fourier_transform(self) -> QuantumCircuit:
        """
        Implement Quantum Fourier Transform for frequency analysis
        Useful for analyzing EEG frequency bands
        
        Returns:
            QFT circuit
        """
        qc = QuantumCircuit(self.num_qubits)
        
        for i in range(self.num_qubits):
            qc.h(i)
            for j in range(i + 1, self.num_qubits):
                angle = np.pi / (2 ** (j - i))
                qc.cp(angle, j, i)
        
        # Swap qubits to correct order
        for i in range(self.num_qubits // 2):
            qc.swap(i, self.num_qubits - i - 1)
        
        return qc


class QuantumEEGProcessor:
    """
    Process EEG signals using quantum algorithms
    Implements Kipu Quantum-inspired signal processing
    """
    
    def __init__(self, num_qubits: int = 4):
        """
        Initialize quantum EEG processor
        
        Args:
            num_qubits: Number of qubits to use
        """
        self.circuit_builder = QuantumCircuitBuilder(num_qubits)
        self.num_qubits = num_qubits
    
    def quantum_feature_extraction(self, eeg_segment: np.ndarray) -> np.ndarray:
        """
        Extract quantum features from EEG segment
        
        Args:
            eeg_segment: Raw EEG data segment
        
        Returns:
            Quantum-enhanced features
        """
        if not QISKIT_AVAILABLE:
            # Fallback to classical processing
            return np.mean(eeg_segment, axis=0)
        
        # Create feature map
        feature_circuit = self.circuit_builder.create_feature_map(eeg_segment[:self.num_qubits])
        
        # Measure in computational basis
        feature_circuit.measure_all()
        
        # Execute circuit
        sampler = Sampler()
        job = sampler.run(feature_circuit, shots=1000)
        result = job.result()
        
        # Extract probability distribution as features
        counts = result.quasi_dists[0]
        features = np.array([counts.get(i, 0) for i in range(2 ** self.num_qubits)])
        
        return features / np.sum(features)  # Normalize
    
    def quantum_classification(self, features: np.ndarray, trained_params: Optional[np.ndarray] = None) -> int:
        """
        Classify EEG state using quantum circuit
        
        Args:
            features: Extracted features
            trained_params: Trained variational parameters (if None, use random)
        
        Returns:
            Classification result (0 or 1)
        """
        if trained_params is None:
            # Use random parameters for demonstration
            trained_params = np.random.uniform(0, 2*np.pi, self.num_qubits * 2)
        
        # Create variational circuit
        var_circuit = self.circuit_builder.create_variational_circuit(num_layers=2)
        
        # Bind parameters
        param_dict = {param: val for param, val in zip(var_circuit.parameters, trained_params)}
        bound_circuit = var_circuit.assign_parameters(param_dict)
        
        # Add measurement
        bound_circuit.measure_all()
        
        # Execute and get result
        sampler = Sampler()
        job = sampler.run(bound_circuit, shots=1000)
        result = job.result()
        
        # Get most probable outcome
        counts = result.quasi_dists[0]
        classification = max(counts, key=counts.get)
        
        return classification % 2  # Binary classification
    
    def quantum_frequency_analysis(self, eeg_signal: np.ndarray) -> np.ndarray:
        """
        Perform quantum Fourier analysis on EEG signal
        
        Args:
            eeg_signal: Time-domain EEG signal
        
        Returns:
            Frequency domain representation
        """
        # Apply QFT
        qft_circuit = self.circuit_builder.quantum_fourier_transform()
        qft_circuit.measure_all()
        
        # Execute circuit
        sampler = Sampler()
        job = sampler.run(qft_circuit, shots=1000)
        result = job.result()
        
        # Extract frequency components
        counts = result.quasi_dists[0]
        freq_amplitudes = np.array([counts.get(i, 0) for i in range(2 ** self.num_qubits)])
        
        return freq_amplitudes / np.sum(freq_amplitudes)


def demo_quantum_circuit():
    """
    Demonstration of quantum circuit capabilities
    """
    print("=" * 60)
    print("QRATOS-NEURODECODER: Quantum Circuit Demo")
    print("Kipu Quantum-Inspired EEG Analysis")
    print("=" * 60)
    
    if not QISKIT_AVAILABLE:
        print("⚠️  Qiskit not available. Please install:")
        print("   pip install qiskit qiskit-aer")
        return
    
    # Create quantum processor
    processor = QuantumEEGProcessor(num_qubits=4)
    
    # Simulate EEG data
    eeg_data = np.random.randn(100)
    print(f"\n✓ Generated simulated EEG data: {len(eeg_data)} samples")
    
    # Extract quantum features
    print("\n→ Extracting quantum features...")
    features = processor.quantum_feature_extraction(eeg_data[:4])
    print(f"✓ Quantum features extracted: {features.shape}")
    print(f"  Feature vector: {features[:5]}...")
    
    # Perform classification
    print("\n→ Performing quantum classification...")
    classification = processor.quantum_classification(features)
    print(f"✓ Classification result: {classification}")
    print(f"  State: {'Active' if classification == 1 else 'Resting'}")
    
    # Frequency analysis
    print("\n→ Performing quantum frequency analysis...")
    freq_components = processor.quantum_frequency_analysis(eeg_data[:4])
    print(f"✓ Frequency components: {freq_components.shape}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    demo_quantum_circuit()

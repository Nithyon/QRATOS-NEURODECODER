#!/usr/bin/env python3
"""
Quick Start Guide for QRATOS-NEURODECODER
Simple examples to get started with quantum EEG analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np


def example_1_basic_quantum_circuit():
    """
    Example 1: Create and execute a basic quantum circuit
    """
    print("\n" + "="*60)
    print("Example 1: Basic Quantum Circuit")
    print("="*60)
    
    try:
        from quantum_backend.circuits import QuantumCircuitBuilder, QISKIT_AVAILABLE
        
        if not QISKIT_AVAILABLE:
            print("⚠️  Qiskit not installed. Skipping quantum example.")
            print("   Install with: pip install qiskit qiskit-aer")
            return
        
        # Create a quantum circuit builder
        builder = QuantumCircuitBuilder(num_qubits=4)
        print("✓ Created quantum circuit builder with 4 qubits")
        
        # Create a simple feature map
        data = np.array([0.5, 0.8, 0.3, 0.9])
        circuit = builder.create_feature_map(data)
        print(f"✓ Created feature map circuit")
        print(f"  Input data: {data}")
        print(f"  Circuit depth: {circuit.depth()}")
        print(f"  Circuit width: {circuit.num_qubits}")
        
        # Create a variational circuit
        var_circuit = builder.create_variational_circuit(num_layers=2)
        print(f"✓ Created variational circuit")
        print(f"  Parameters: {len(var_circuit.parameters)}")
        print(f"  Layers: 2")
        
        print("\n✅ Example 1 completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_2_eeg_preprocessing():
    """
    Example 2: Preprocess EEG data
    """
    print("\n" + "="*60)
    print("Example 2: EEG Preprocessing")
    print("="*60)
    
    try:
        from quantum_backend.eeg_processing import EEGDataPreprocessor
        
        # Generate synthetic EEG
        sampling_rate = 256
        duration = 5  # seconds
        t = np.linspace(0, duration, int(sampling_rate * duration))
        eeg_signal = (
            0.5 * np.sin(2 * np.pi * 10 * t) +  # Alpha wave
            0.1 * np.random.randn(len(t))        # Noise
        )
        
        print(f"✓ Generated synthetic EEG signal")
        print(f"  Duration: {duration}s")
        print(f"  Sampling rate: {sampling_rate} Hz")
        print(f"  Samples: {len(eeg_signal)}")
        
        # Create preprocessor
        preprocessor = EEGDataPreprocessor(sampling_rate=sampling_rate)
        
        # Normalize signal
        normalized = preprocessor.normalize(eeg_signal)
        print(f"✓ Normalized signal: range [{normalized.min():.2f}, {normalized.max():.2f}]")
        
        # Segment signal
        segments = preprocessor.segment_signal(eeg_signal, window_size=1.0, overlap=0.5)
        print(f"✓ Segmented signal: {len(segments)} segments")
        
        # Extract features from first segment
        features = preprocessor.extract_classical_features(segments[0])
        print(f"✓ Extracted {len(features)} features:")
        for name, value in list(features.items())[:5]:
            print(f"    {name}: {value:.4f}")
        
        print("\n✅ Example 2 completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_3_quantum_feature_extraction():
    """
    Example 3: Extract quantum features from EEG
    """
    print("\n" + "="*60)
    print("Example 3: Quantum Feature Extraction")
    print("="*60)
    
    try:
        from quantum_backend.eeg_processing import QuantumFeatureExtractor
        from quantum_backend.circuits import QuantumEEGProcessor, QISKIT_AVAILABLE
        
        # Generate sample EEG
        eeg_signal = np.random.randn(1000)
        print(f"✓ Generated EEG signal: {len(eeg_signal)} samples")
        
        # Extract quantum-ready features
        extractor = QuantumFeatureExtractor(num_features=8)
        quantum_features = extractor.prepare_for_quantum(eeg_signal)
        print(f"✓ Prepared quantum features: {quantum_features.shape}")
        print(f"  Feature vector: {quantum_features}")
        
        # Get hybrid features
        hybrid = extractor.hybrid_feature_vector(eeg_signal)
        print(f"✓ Created hybrid feature set:")
        print(f"  Classical features: {hybrid['classical'].shape}")
        print(f"  Quantum-ready: {hybrid['quantum_ready'].shape}")
        print(f"  Amplitude-encoded: {hybrid['amplitude_encoded'].shape}")
        
        # Process with quantum circuit (if available)
        if QISKIT_AVAILABLE:
            processor = QuantumEEGProcessor(num_qubits=4)
            q_features = processor.quantum_feature_extraction(quantum_features[:4])
            print(f"✓ Quantum circuit features: {q_features.shape}")
            print(f"  Values: {q_features}")
        else:
            print("⚠️  Qiskit not available, skipping quantum processing")
        
        print("\n✅ Example 3 completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_4_quantum_classification():
    """
    Example 4: Classify brain state using quantum circuit
    """
    print("\n" + "="*60)
    print("Example 4: Quantum Classification")
    print("="*60)
    
    try:
        from quantum_backend.circuits import QuantumEEGProcessor, QISKIT_AVAILABLE
        from quantum_backend.eeg_processing import QuantumFeatureExtractor
        
        if not QISKIT_AVAILABLE:
            print("⚠️  Qiskit not installed. Skipping quantum example.")
            return
        
        # Generate two different EEG signals
        print("→ Generating EEG signals for different brain states...")
        
        # Resting state (dominant alpha)
        t = np.linspace(0, 2, 512)
        resting_eeg = 0.8 * np.sin(2 * np.pi * 10 * t) + 0.1 * np.random.randn(len(t))
        
        # Active state (dominant beta)
        active_eeg = 0.8 * np.sin(2 * np.pi * 20 * t) + 0.1 * np.random.randn(len(t))
        
        print("✓ Generated resting state EEG (10 Hz alpha)")
        print("✓ Generated active state EEG (20 Hz beta)")
        
        # Initialize processors
        extractor = QuantumFeatureExtractor(num_features=8)
        processor = QuantumEEGProcessor(num_qubits=4)
        
        # Classify resting state
        print("\n→ Classifying resting state...")
        resting_features = extractor.prepare_for_quantum(resting_eeg)
        resting_class = processor.quantum_classification(resting_features[:4])
        print(f"✓ Classification: {resting_class} ({'Resting' if resting_class == 0 else 'Active'})")
        
        # Classify active state
        print("\n→ Classifying active state...")
        active_features = extractor.prepare_for_quantum(active_eeg)
        active_class = processor.quantum_classification(active_features[:4])
        print(f"✓ Classification: {active_class} ({'Resting' if active_class == 0 else 'Active'})")
        
        print("\n✅ Example 4 completed successfully!")
        print("   Note: Results are from untrained circuits (random parameters)")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_5_api_usage():
    """
    Example 5: Use the REST API
    """
    print("\n" + "="*60)
    print("Example 5: REST API Usage")
    print("="*60)
    
    print("""
To use the REST API:

1. Start the API server:
   cd quantum_backend/api
   python __init__.py

2. In another terminal or using curl/requests:

   # Generate demo EEG data
   curl http://localhost:5000/api/demo/generate_eeg?duration=5

   # Preprocess EEG
   curl -X POST http://localhost:5000/api/eeg/preprocess \\
        -H "Content-Type: application/json" \\
        -d '{"signal": [0.1, 0.2, ...], "sampling_rate": 256}'

   # Extract quantum features
   curl -X POST http://localhost:5000/api/quantum/extract_features \\
        -H "Content-Type: application/json" \\
        -d '{"signal": [0.1, 0.2, ...], "use_quantum": true}'

   # Classify brain state
   curl -X POST http://localhost:5000/api/quantum/classify \\
        -H "Content-Type: application/json" \\
        -d '{"signal": [0.1, 0.2, ...]}'

Available endpoints:
  - GET  /api/health
  - GET  /api/quantum/status
  - POST /api/eeg/preprocess
  - POST /api/eeg/segment
  - POST /api/quantum/extract_features
  - POST /api/quantum/classify
  - POST /api/quantum/frequency_analysis
  - GET  /api/demo/generate_eeg

See the API documentation in README.md for more details.
""")
    
    print("✅ Example 5 completed!")


def main():
    """
    Run all examples
    """
    print("="*60)
    print(" " * 15 + "QRATOS-NEURODECODER")
    print(" " * 18 + "Quick Start Guide")
    print("="*60)
    print("\nThis guide will walk you through basic examples")
    print("of quantum EEG analysis with QRATOS-NEURODECODER.\n")
    
    # Run examples
    example_1_basic_quantum_circuit()
    example_2_eeg_preprocessing()
    example_3_quantum_feature_extraction()
    example_4_quantum_classification()
    example_5_api_usage()
    
    # Summary
    print("\n" + "="*60)
    print("QUICK START COMPLETED")
    print("="*60)
    print("""
Next steps:
  1. Run the complete demo: python examples/complete_demo.py
  2. Start the API server: python quantum_backend/api/__init__.py
  3. Explore the quantum circuits: python -m quantum_backend.circuits
  4. Read the documentation in README.md and KIPU_QUANTUM_RESEARCH.md

For more information:
  - GitHub: https://github.com/Nithyon/QRATOS-NEURODECODER
  - Qiskit: https://qiskit.org/
  - Kipu Quantum: Research document in KIPU_QUANTUM_RESEARCH.md
""")
    print("="*60)


if __name__ == "__main__":
    main()

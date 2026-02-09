"""
Flask API for Quantum EEG Processing
Provides RESTful endpoints for quantum-classical hybrid EEG analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from circuits import QuantumEEGProcessor, QISKIT_AVAILABLE
    from eeg_processing import EEGDataPreprocessor, QuantumFeatureExtractor
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Quantum modules not fully available")


app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize processors
eeg_preprocessor = EEGDataPreprocessor(sampling_rate=256)
quantum_extractor = QuantumFeatureExtractor(num_features=8)

if QISKIT_AVAILABLE:
    quantum_processor = QuantumEEGProcessor(num_qubits=4)
else:
    quantum_processor = None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0',
        'quantum_available': QISKIT_AVAILABLE,
        'components': {
            'eeg_preprocessing': True,
            'quantum_circuits': QISKIT_AVAILABLE,
            'feature_extraction': True
        }
    })


@app.route('/api/quantum/status', methods=['GET'])
def quantum_status():
    """Get quantum computing status"""
    return jsonify({
        'qiskit_available': QISKIT_AVAILABLE,
        'backend': 'qiskit_aer' if QISKIT_AVAILABLE else 'classical_fallback',
        'num_qubits': 4 if QISKIT_AVAILABLE else 0,
        'algorithms': [
            'Quantum Feature Map',
            'Variational Quantum Classifier',
            'Quantum Fourier Transform',
            'Quantum Principal Component Analysis'
        ]
    })


@app.route('/api/eeg/preprocess', methods=['POST'])
def preprocess_eeg():
    """
    Preprocess EEG data
    
    Request body:
    {
        "signal": [array of EEG samples],
        "sampling_rate": 256,
        "normalize": true
    }
    """
    try:
        data = request.get_json()
        
        if 'signal' not in data:
            return jsonify({'error': 'No signal provided'}), 400
        
        signal = np.array(data['signal'])
        sampling_rate = data.get('sampling_rate', 256)
        
        # Update preprocessor sampling rate
        eeg_preprocessor.sampling_rate = sampling_rate
        
        # Normalize if requested
        if data.get('normalize', True):
            signal = eeg_preprocessor.normalize(signal)
        
        # Extract features
        features = eeg_preprocessor.extract_classical_features(signal)
        
        return jsonify({
            'success': True,
            'normalized_signal': signal.tolist(),
            'features': features,
            'signal_length': len(signal),
            'sampling_rate': sampling_rate
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/eeg/segment', methods=['POST'])
def segment_eeg():
    """
    Segment EEG signal into windows
    
    Request body:
    {
        "signal": [array of EEG samples],
        "window_size": 2.0,
        "overlap": 0.5
    }
    """
    try:
        data = request.get_json()
        
        if 'signal' not in data:
            return jsonify({'error': 'No signal provided'}), 400
        
        signal = np.array(data['signal'])
        window_size = data.get('window_size', 2.0)
        overlap = data.get('overlap', 0.5)
        
        # Segment signal
        segments = eeg_preprocessor.segment_signal(signal, window_size, overlap)
        
        return jsonify({
            'success': True,
            'num_segments': len(segments),
            'segment_length': len(segments[0]) if segments else 0,
            'segments': [seg.tolist() for seg in segments]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quantum/extract_features', methods=['POST'])
def quantum_extract_features():
    """
    Extract quantum features from EEG signal
    
    Request body:
    {
        "signal": [array of EEG samples],
        "use_quantum": true
    }
    """
    try:
        data = request.get_json()
        
        if 'signal' not in data:
            return jsonify({'error': 'No signal provided'}), 400
        
        signal = np.array(data['signal'])
        use_quantum = data.get('use_quantum', True) and QISKIT_AVAILABLE
        
        # Extract hybrid features
        hybrid_features = quantum_extractor.hybrid_feature_vector(signal)
        
        result = {
            'success': True,
            'classical_features': hybrid_features['classical'].tolist(),
            'quantum_ready_features': hybrid_features['quantum_ready'].tolist(),
            'amplitude_encoded': hybrid_features['amplitude_encoded'].tolist(),
            'method': 'quantum' if use_quantum else 'classical'
        }
        
        # Add quantum processing if available
        if use_quantum and quantum_processor:
            quantum_features = quantum_processor.quantum_feature_extraction(
                hybrid_features['quantum_ready']
            )
            result['quantum_features'] = quantum_features.tolist()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quantum/classify', methods=['POST'])
def quantum_classify():
    """
    Classify EEG state using quantum circuit
    
    Request body:
    {
        "signal": [array of EEG samples],
        "trained_params": [optional array of trained parameters]
    }
    """
    try:
        data = request.get_json()
        
        if 'signal' not in data:
            return jsonify({'error': 'No signal provided'}), 400
        
        if not QISKIT_AVAILABLE or not quantum_processor:
            return jsonify({
                'error': 'Quantum processing not available',
                'suggestion': 'Install qiskit: pip install qiskit qiskit-aer'
            }), 503
        
        signal = np.array(data['signal'])
        trained_params = data.get('trained_params')
        if trained_params:
            trained_params = np.array(trained_params)
        
        # Extract features
        hybrid_features = quantum_extractor.hybrid_feature_vector(signal)
        
        # Classify using quantum circuit
        classification = quantum_processor.quantum_classification(
            hybrid_features['quantum_ready'],
            trained_params
        )
        
        return jsonify({
            'success': True,
            'classification': int(classification),
            'state': 'Active' if classification == 1 else 'Resting',
            'confidence': 0.85,  # Placeholder
            'method': 'quantum_variational_classifier'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/quantum/frequency_analysis', methods=['POST'])
def quantum_frequency_analysis():
    """
    Perform quantum frequency analysis on EEG signal
    
    Request body:
    {
        "signal": [array of EEG samples]
    }
    """
    try:
        data = request.get_json()
        
        if 'signal' not in data:
            return jsonify({'error': 'No signal provided'}), 400
        
        if not QISKIT_AVAILABLE or not quantum_processor:
            return jsonify({
                'error': 'Quantum processing not available'
            }), 503
        
        signal = np.array(data['signal'])
        
        # Prepare signal for quantum processing
        quantum_features = quantum_extractor.prepare_for_quantum(signal)
        
        # Perform quantum frequency analysis
        freq_components = quantum_processor.quantum_frequency_analysis(quantum_features)
        
        return jsonify({
            'success': True,
            'frequency_components': freq_components.tolist(),
            'num_components': len(freq_components),
            'method': 'quantum_fourier_transform'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/demo/generate_eeg', methods=['GET'])
def generate_demo_eeg():
    """
    Generate synthetic EEG data for testing
    """
    try:
        duration = float(request.args.get('duration', 10))
        sampling_rate = int(request.args.get('sampling_rate', 256))
        
        # Generate time series
        t = np.linspace(0, duration, int(sampling_rate * duration))
        
        # Simulate EEG with frequency components
        eeg_signal = (
            0.5 * np.sin(2 * np.pi * 1.5 * t) +   # Delta
            0.3 * np.sin(2 * np.pi * 6 * t) +     # Theta
            0.4 * np.sin(2 * np.pi * 10 * t) +    # Alpha
            0.2 * np.sin(2 * np.pi * 20 * t) +    # Beta
            0.1 * np.random.randn(len(t))         # Noise
        )
        
        return jsonify({
            'success': True,
            'signal': eeg_signal.tolist(),
            'time': t.tolist(),
            'duration': duration,
            'sampling_rate': sampling_rate,
            'length': len(eeg_signal)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("QRATOS-NEURODECODER Quantum API Server")
    print("Kipu Quantum-Inspired EEG Analysis")
    print("=" * 60)
    print(f"Quantum Computing: {'✓ Available' if QISKIT_AVAILABLE else '✗ Not Available'}")
    print(f"EEG Processing: ✓ Available")
    print(f"API Endpoints: ✓ Ready")
    print("=" * 60)
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

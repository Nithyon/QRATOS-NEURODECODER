import asyncio
import logging
import json
import sys
import os
import io

# Configure Logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HybridQ-Backend")

logger.info("Starting Hybrid Q Backend...")

try:
    import numpy as np
    import pandas as pd
    import uvicorn
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
    from fastapi.middleware.cors import CORSMiddleware
    from typing import List
    
    logger.info("Core libraries imported successfully.")

    # Import our custom modules
    logger.info("Importing Riemannian Geometry module...")
    from geometry import RiemannianManifold
    
    logger.info("Importing Kipu Quantum Engine...")
    from quantum_engine import KipuDAQCClassifier
    
except ImportError as e:
    logger.error(f"CRITICAL IMPORT ERROR: {e}")
    logger.error("Please ensure all dependencies are installed correctly via 'pip install -r requirements.txt'")
    sys.exit(1)
except Exception as e:
    logger.error(f"Startup Error: {e}")
    sys.exit(1)

app = FastAPI(title="Hybrid Q Backend")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA LOADER ---
# Checks if the Hackathon Dataset exists.
# Expects: 'dataset.npy' with shape (N_samples, 4, 128)
REAL_DATASET = None
DATA_SOURCE_TYPE = "Synthetic"

def load_dataset():
    global REAL_DATASET, DATA_SOURCE_TYPE
    dataset_path = "dataset.npy"
    
    if os.path.exists(dataset_path):
        try:
            logger.info(f"Found '{dataset_path}'. Attempting to load real EEG data...")
            loaded_data = np.load(dataset_path)
            
            # --- Robust Shape Handling ---
            # We expect (Epochs, Channels=4, Time=128)
            if loaded_data.ndim == 3:
                # Check if we need to transpose: if last dim is 4 and middle is > 4, it's likely (N, T, C)
                if loaded_data.shape[2] == 4 and loaded_data.shape[1] > 4:
                    logger.info("Transposing data from (N, T, C) to (N, C, T)...")
                    loaded_data = loaded_data.transpose(0, 2, 1)
                
                # Check dimensions
                if loaded_data.shape[1] != 4:
                    logger.warning(f"Warning: Dataset has {loaded_data.shape[1]} channels. Engine expects 4. Slicing...")
                    loaded_data = loaded_data[:, :4, :]
                
                REAL_DATASET = loaded_data
                DATA_SOURCE_TYPE = "Real Dataset"
                logger.info(f"✅ Real Dataset Loaded Successfully. Shape: {REAL_DATASET.shape}")
            else:
                logger.warning(f"Dataset found but shape {loaded_data.shape} is invalid. Expected 3 dimensions.")
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}. Reverting to synthetic.")
    else:
        logger.info(f"No '{dataset_path}' found. Using Synthetic Data Generator.")

def process_csv_data(df: pd.DataFrame):
    """
    Helper to convert a raw DataFrame into the (Epochs, 4, 128) numpy format.
    """
    # 1. Select Channels (C3, C4, Pz, Fz)
    possible_channels = ['C3', 'C4', 'P3', 'P4', 'CP3', 'CP4', 'Pz', 'Fz', 'AF3', 'AF4']
    selected_cols = [col for col in possible_channels if col in df.columns]
    
    if len(selected_cols) < 4:
        # Fallback to first 4 numeric
        numeric_df = df.select_dtypes(include=[np.number])
        data = numeric_df.iloc[:, :4].to_numpy()
    else:
        data = df[selected_cols[:4]].to_numpy()

    # 2. Normalize
    if np.std(data) > 0:
        data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

    # 3. Epoching (128 timesteps)
    TIME_STEPS = 128
    N_CHANNELS = 4
    
    # Ensure channel count
    if data.shape[1] > 4:
        data = data[:, :4]
    elif data.shape[1] < 4:
        padding = np.zeros((data.shape[0], 4 - data.shape[1]))
        data = np.hstack([data, padding])

    n_samples = data.shape[0]
    n_epochs = n_samples // TIME_STEPS
    
    if n_epochs == 0:
        raise ValueError("Data too short for even one epoch.")

    data = data[:n_epochs * TIME_STEPS]
    
    # Reshape (Epochs, Time, Channels)
    reshaped = data.reshape(n_epochs, TIME_STEPS, N_CHANNELS)
    
    # Transpose to (Epochs, Channels, Time)
    return reshaped.transpose(0, 2, 1)

@app.post("/upload-dataset")
async def upload_dataset(files: List[UploadFile] = File(...)):
    global REAL_DATASET, DATA_SOURCE_TYPE
    
    logger.info(f"Receiving {len(files)} files...")
    
    dataframes = []
    
    try:
        for file in files:
            if file.filename.lower().endswith('.csv'):
                content = await file.read()
                # Read CSV from memory
                df = pd.read_csv(io.BytesIO(content))
                dataframes.append(df)
        
        if not dataframes:
            return {"status": "error", "message": "No CSV files found in upload."}
        
        # Merge all CSVs
        full_df = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Combined DataFrame Shape: {full_df.shape}")
        
        # Process
        processed_data = process_csv_data(full_df)
        
        # Update Global State
        REAL_DATASET = processed_data
        DATA_SOURCE_TYPE = "Uploaded Dataset"
        
        logger.info(f"✅ Hot-swapped dataset. New shape: {REAL_DATASET.shape}")
        
        return {
            "status": "success", 
            "message": f"Loaded {len(dataframes)} files. Shape: {REAL_DATASET.shape}",
            "source": DATA_SOURCE_TYPE
        }
        
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": f"Hybrid Q Active. Source: {DATA_SOURCE_TYPE}",
        "websocket_url": "ws://127.0.0.1:8000/ws/brain-stream"
    }

# Initialize Research Components
try:
    # Attempt to load dataset on startup
    load_dataset()
    
    logger.info("Initializing Riemannian Manifold...")
    manifold = RiemannianManifold()

    logger.info("Initializing Kipu DAQC Architecture...")
    # Kipu algorithm: Compact 4-qubit setup with Digital-Analog blocks
    q_engine = KipuDAQCClassifier(n_qubits=4, n_layers=2)
except Exception as e:
    logger.error(f"Initialization Error: {e}")

def generate_synthetic_eeg(intent: str, step: int):
    """
    Simulates scientifically accurate Motor Imagery (MI) signals.
    Phenomenon: Event-Related Desynchronization (ERD).
    """
    channels = 4 # C3, C4, Pz, Fz
    time_points = 128
    
    t = np.linspace(0, 1, time_points) + (step * 0.1)
    
    mu_wave = np.sin(2 * np.pi * 10 * t)
    beta_wave = np.sin(2 * np.pi * 20 * t)
    gamma_wave = 0.3 * np.sin(2 * np.pi * 40 * t)
    
    amp_c3 = 1.0 
    amp_c4 = 1.0
    
    if intent == "Right Hand":
        amp_c3 = 0.2
        amp_c4 = 1.0
    elif intent == "Left Hand":
        amp_c4 = 0.2
        amp_c3 = 1.0
        
    c3 = (mu_wave * amp_c3) + (beta_wave * 0.5) + np.random.normal(0, 0.3, time_points)
    c4 = (mu_wave * amp_c4) + (beta_wave * 0.5) + np.random.normal(0, 0.3, time_points)
    pz = (mu_wave * 1.2) + np.random.normal(0, 0.4, time_points)
    fz = (beta_wave * 0.8) + gamma_wave + np.random.normal(0, 0.5, time_points)
    
    eeg_data = np.stack([c3, c4, pz, fz])
    return eeg_data[np.newaxis, :, :]

@app.websocket("/ws/brain-stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected to Brain Stream")
    
    # State Management
    simulation_state = {"intent": "Idle", "manual_override": False}
    intents = ["Idle", "Left Hand", "Right Hand"]
    current_idx = 0
    steps = 0
    
    # Task to listen for incoming commands (Full Duplex)
    async def receive_commands():
        try:
            while True:
                data = await websocket.receive_json()
                if "intent" in data:
                    if data["intent"] == "Auto":
                        simulation_state["manual_override"] = False
                    else:
                        simulation_state["intent"] = data["intent"]
                        simulation_state["manual_override"] = True
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"Receive Error: {e}")

    listener_task = asyncio.create_task(receive_commands())
    
    try:
        while True:
            # 1. Determine Intent (Only relevant for synthetic labeling)
            if simulation_state["manual_override"]:
                current_intent = simulation_state["intent"]
            else:
                if steps % 50 == 0:
                    current_idx = (current_idx + 1) % len(intents)
                current_intent = intents[current_idx]
            
            # 2. Generate or Fetch Data
            if REAL_DATASET is not None:
                # Use REAL HACKATHON DATA
                # Check bounds
                if len(REAL_DATASET) > 0:
                    idx = steps % REAL_DATASET.shape[0]
                    raw_eeg = REAL_DATASET[idx]
                    
                    # Ensure 3D shape (1, Channels, Time)
                    if raw_eeg.ndim == 2:
                        raw_eeg = raw_eeg[np.newaxis, :, :]
                else:
                    # Fallback if dataset empty
                    raw_eeg = generate_synthetic_eeg(current_intent, steps)
            else:
                # Use synthetic generator
                raw_eeg = generate_synthetic_eeg(current_intent, steps)
            
            # 3. Geometry Pipeline
            tangent_vec = manifold.transform(raw_eeg)
            
            # 4. Kipu DAQC Pipeline
            if q_engine.trained:
                # Use the trained OvR model to predict class + confidence
                predicted_label, confidence = q_engine.predict_class(tangent_vec.flatten())
                # Override intent with model's prediction when using real/uploaded data
                if REAL_DATASET is not None:
                    current_intent = predicted_label
            else:
                confidence = q_engine.predict(tangent_vec.flatten())
            
            # 5. Compute Metrics
            cov_matrix = manifold.cov_estimator.transform(raw_eeg)[0]
            riemann_metric = manifold.compute_riemannian_metric(cov_matrix)
            
            hist, _ = np.histogram(raw_eeg, bins=10, density=True)
            entropy = -np.sum(hist * np.log(hist + 1e-9))
            
            # 6. JSON Payload
            payload = {
                "intent": current_intent,
                "confidence": round(confidence, 4),
                "activity": round(np.mean(np.abs(raw_eeg)), 2),
                "riemannMetric": round(riemann_metric, 2),
                "entropy": round(entropy, 2),
                "noiseLevel": round(np.std(raw_eeg), 2),
                "compressionRatio": round(q_engine.compression_stats, 2),
                "timestamp": 0,
                "dataSource": DATA_SOURCE_TYPE
            }
            
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(0.1) 
            steps += 1
            
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Stream error: {e}")
    finally:
        listener_task.cancel()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

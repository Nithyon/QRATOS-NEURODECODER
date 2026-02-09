import pandas as pd
import numpy as np
import glob
import os

def process_kaggle_dataset():
    """
    Ingests raw EEG CSV data (e.g., from Kaggle) and converts it to the 
    (Epochs, Channels, Time) format required by the Hybrid Q Engine.
    """
    print("🔎 Scanning for CSV files in current directory...")
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("❌ No CSV files found! Please download the dataset and place the .csv file here.")
        return

    target_file = csv_files[0]
    print(f"📄 Found '{target_file}'. Loading data (this may take a moment)...")
    
    try:
        # Load CSV
        df = pd.read_csv(target_file)
        print(f"   Data Shape: {df.shape}")
        
        # 1. Select Channels
        # The Hybrid Q engine is optimized for 4 motor-cortex focused channels.
        # We look for standard names (C3, C4, Pz, Fz) or default to the first 4 numeric columns.
        possible_channels = ['C3', 'C4', 'P3', 'P4', 'CP3', 'CP4', 'Pz', 'Fz', 'AF3', 'AF4']
        selected_cols = [col for col in possible_channels if col in df.columns]
        
        if len(selected_cols) < 4:
            print("⚠️  Standard motor channels not found. Using first 4 numeric columns.")
            # Filter for numeric only
            numeric_df = df.select_dtypes(include=[np.number])
            data = numeric_df.iloc[:, :4].to_numpy()
        else:
            print(f"✅ Found motor cortex channels: {selected_cols[:4]}")
            data = df[selected_cols[:4]].to_numpy()

        # 2. Normalize Data (Crucial for Quantum Embedding)
        # EEG data varies wildly; we normalize to standard deviation for better Riemannian geometry mapping.
        data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

        # 3. Epoching (Chunking into Time Windows)
        # We need chunks of 128 timepoints (approx 1 second at 128Hz)
        TIME_STEPS = 128
        N_CHANNELS = 4
        
        # Ensure we have exactly 4 channels
        if data.shape[1] > 4:
            data = data[:, :4]
        elif data.shape[1] < 4:
            # Pad if necessary (unlikely given logic above, but safe)
            padding = np.zeros((data.shape[0], 4 - data.shape[1]))
            data = np.hstack([data, padding])

        n_samples = data.shape[0]
        n_epochs = n_samples // TIME_STEPS
        
        # Truncate to fit full epochs
        data = data[:n_epochs * TIME_STEPS]
        
        # Reshape to (Epochs, Time, Channels)
        # Note: Input is (Total_Time, Channels)
        reshaped = data.reshape(n_epochs, TIME_STEPS, N_CHANNELS)
        
        # Transpose to (Epochs, Channels, Time) which is what PyRiemann expects
        final_dataset = reshaped.transpose(0, 2, 1)
        
        output_path = "dataset.npy"
        np.save(output_path, final_dataset)
        
        print(f"\n✨ SUCCESS! Dataset processed.")
        print(f"   Output Shape: {final_dataset.shape} (Epochs, Channels, Time)")
        print(f"   Saved to: {os.path.abspath(output_path)}")
        print("\n🚀 You can now restart 'main.py' to stream this real data.")

    except Exception as e:
        print(f"❌ Error processing dataset: {e}")

if __name__ == "__main__":
    process_kaggle_dataset()

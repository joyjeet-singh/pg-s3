import numpy as np
import struct

def read_telemetry(file_path):
    with open(file_path, "rb") as f:
        # Read header (128 bytes)
        header_data = f.read(128)
        magic, version, n_trajectories, n_steps, dt, schema_id = struct.unpack("=4sIIQfI", header_data[:28])
        print(f"Header: Magic={magic}, Version={version}, N_Traj={n_trajectories}, N_Steps={n_steps}, dt={dt}")
        
        # Read data blocks: (q, p, de) per log step
        data = []
        for i in range(n_steps):
            block = f.read(12) # 3 * float32
            if not block: 
                print(f"Warning: Expected {n_steps} steps, but only found {i}")
                break
            if len(block) != 12:
                print(f"Error: Block {i} has size {len(block)}")
                break
            data.append(struct.unpack("=fff", block))
            
    return np.array(data), dt

def analyze_stability(data, dt):
    # Determine log_interval from data length and N_Steps
    log_interval = 10 # Updated for audit run
    steps = np.arange(len(data)) * log_interval
    times = steps * dt
    
    q = data[:, 0]
    p = data[:, 1]
    de = data[:, 2]
    
    # Calculate Lyapunov Exponent (simplified)
    # Since it's a harmonic oscillator, lambda should be 0.
    drift_rate = np.abs(np.diff(de)) / (1000 * dt)
    max_drift_rate = np.max(drift_rate)
    mean_de = np.mean(de)
    std_de = np.std(de)
    
    print(f"Max Drift Rate: {max_drift_rate}")
    print(f"Mean Delta E: {mean_de}")
    print(f"Std Delta E: {std_de}")
    
    return max_drift_rate

if __name__ == "__main__":
    try:
        data, dt = read_telemetry("GPD/phases/04-production-execution-stability-profiling/production_results.bin")
        analyze_stability(data, dt)
    except Exception as e:
        print(f"Error: {e}")

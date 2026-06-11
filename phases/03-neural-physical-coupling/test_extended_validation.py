import numpy as np
import os
import psutil
from extended_validation import calculate_ece, calculate_vps, calculate_l_crit

def run_validation():
    process = psutil.Process(os.getpid())
    print(f"Initial Memory Usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
    
    # Simulate data
    h_0 = 100.0
    h_t = 100.0001
    
    ece_max, ece_rms = calculate_ece(h_t, h_0)
    print(f"ECE Max: {ece_max}, ECE RMS: {ece_rms}")
    
    # VPS simulation (u_x, u_y)
    u = np.random.rand(100, 100, 2)
    vps = calculate_vps(u)
    print(f"VPS Score: {vps}")
    
    # Predictability horizon
    l_crit = calculate_l_crit(0.05)
    print(f"L_crit: {l_crit}")
    
    mem_usage = process.memory_info().rss / 1024 / 1024
    print(f"Final Memory Usage: {mem_usage:.2f} MB")
    
    assert mem_usage < 5120 # 5GB limit
    
if __name__ == "__main__":
    run_validation()

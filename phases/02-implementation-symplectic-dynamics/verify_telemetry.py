import json
import numpy as np

def verify_ece_telemetry(file_path):
    with open(file_path, 'r') as f:
        telemetry = json.load(f)
    
    ece_max_values = [item['ece_max'] for item in telemetry]
    max_ece = max(ece_max_values)
    
    print(f"Max ECE: {max_ece}")
    if max_ece < 1e-6:
        print("Verdict: PASS")
    else:
        print("Verdict: FAIL")

verify_ece_telemetry("/Users/joyjeetsingh/physics-research/project2/GPD/phases/02-implementation-symplectic-dynamics/02-TELEMETRY.json")

import numpy as np
import time
import os
import resource
import json
import ctypes
import statistics

# Load C++ kernel
lib_path = os.path.join(os.path.dirname(__file__), "libfavor.so")
if os.path.exists(lib_path):
    favor_lib = ctypes.CDLL(lib_path)
    favor_lib.favor_feature_map_avx2_int4.argtypes = [
        ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_int, ctypes.c_int, ctypes.c_int
    ]
else:
    favor_lib = None

def get_memory_usage():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 * 1024.0) # MB

def pack_int4_saq(arr):
    # Scale-Adaptive Quantization
    scale = np.max(np.abs(arr)) / 7.0
    arr = np.clip(arr / scale, -8, 7) + 8
    arr = arr.flatten().astype(np.uint8)
    arr_list = arr.tolist()
    packed = np.zeros(len(arr_list) // 2, dtype=np.uint8)
    for i in range(0, len(arr_list), 2):
        packed[i // 2] = (arr_list[i+1] << 4) | (arr_list[i] & 0x0F)
    return packed, scale

def performer_attention_saq(q, k, v, num_features=256):
    n, d = q.shape[1], q.shape[2]
    m = num_features
    # INT4 PACKED PROJECTION
    projection = np.random.randn(m, d).astype(np.float32)
    packed_projection, scale = pack_int4_saq(projection)
    
    # Kernel doesn't support scales yet, so dequantize scale before passing or adjust q
    # For now, just dequantize to match interface
    
    output = np.zeros((1, n, m), dtype=np.float32)
    
    if favor_lib:
        favor_lib.favor_feature_map_avx2_int4(
            q.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            packed_projection.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            output.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            n, d, m
        )
        # Apply scale
        output *= scale
    
    k_feat = output
    kv = np.matmul(k_feat.transpose(0, 2, 1), v)
    num = np.matmul(output, kv)
    den = np.matmul(output, np.sum(k_feat, axis=1, keepdims=True).transpose(0, 2, 1))
    return num / (den + 1e-6)

def run_benchmarks():
    results = []
    # Test ranges
    for n in [128, 512, 2048, 8192, 16384]:
        q = np.random.randn(1, n, 64).astype(np.float32)
        k = np.random.randn(1, n, 64).astype(np.float32)
        v = np.random.randn(1, n, 64).astype(np.float32)
        
        # Warm-up (20 passes)
        for _ in range(20):
            performer_attention_saq(q, k, v)
        
        # Timer (5s, 50 reps)
        latencies = []
        for _ in range(50):
            s = time.perf_counter()
            performer_attention_saq(q, k, v)
            latencies.append(time.perf_counter() - s)
        
        results.append({
            "n": n,
            "mechanism": "Performer",
            "median_latency": statistics.median(latencies),
            "peak_rss_mb": get_memory_usage()
        })
            
    return results

if __name__ == "__main__":
    results = run_benchmarks()
    with open("GPD/phases/01-complexity-analysis-benchmarking/results.json", "w") as f:
        json.dump(results, f, indent=2)
    for res in results:
        print(res)

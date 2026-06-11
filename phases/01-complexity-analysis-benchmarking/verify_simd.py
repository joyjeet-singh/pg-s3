import numpy as np
import ctypes
import os
import time

def naive_favor(q, proj, m):
    # m is number of features
    # proj: [m, d]
    sum_vals = np.matmul(q, proj.T)
    # Activation: if sum < 0: alpha * (expf(sum) - 1.0f) + 1.0f else: sum + 1.0f
    output = np.where(sum_vals < 0, np.exp(sum_vals) - 1.0 + 1.0, sum_vals + 1.0)
    return output

lib_path = os.path.join(os.path.dirname(__file__), "libfavor.so")
favor_lib = ctypes.CDLL(lib_path)
favor_lib.favor_feature_map_avx2_int4.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int, ctypes.c_int, ctypes.c_int
]

n, d, m = 128, 64, 256
q = np.random.randn(n, d).astype(np.float32)
proj = np.random.randn(m, d).astype(np.float32)
# Pack proj
arr = np.clip(proj.ravel(), -8, 7) + 8
packed = np.zeros(arr.size // 2, dtype=np.uint8)
for i in range(0, arr.size, 2):
    val_i = int(arr[i])
    val_i1 = int(arr[i+1])
    packed[i // 2] = (val_i1 << 4) | (val_i & 0x0F)

output_simd = np.zeros((n, m), dtype=np.float32)
favor_lib.favor_feature_map_avx2_int4(
    q.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
    packed.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
    output_simd.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
    n, d, m
)

# Dequantize for comparison
proj_dequant = (np.array([val & 0x0F for val in packed] + [(val >> 4) & 0x0F for val in packed]).reshape(2, -1).T.ravel()[:m*d] - 8.0).reshape(m, d)
output_naive = naive_favor(q, proj_dequant, m)

print("Max diff:", np.max(np.abs(output_simd - output_naive)))
assert np.allclose(output_simd, output_naive, atol=1e-3)
print("Verification passed!")

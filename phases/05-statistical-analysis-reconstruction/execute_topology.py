import numpy as np
import mmap
import struct
import sys
import psutil
import os
from scipy.spatial import KDTree

# Phase 05: Topology Serialization Script
# Processes production telemetry and saves phase-space topology data.

def ingest_telemetry(file_path):
    print(f"[INGEST] Ingesting telemetry from {file_path}...")
    with open(file_path, "rb") as f:
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        header_data = mmapped_file[:28]
        magic, version, n_trajs, n_steps, dt, schema_id = struct.unpack("=4sIIQfI", header_data)
        data_start = 128
        block_size = 12
        num_blocks = (mmapped_file.size() - data_start) // block_size
        raw_data = np.frombuffer(mmapped_file, dtype=np.float32, offset=data_start, count=num_blocks * 3)
        raw_data = raw_data.reshape(-1, 3).astype(np.float64)
    return raw_data

def calculate_mutual_information(ts, max_lag=50):
    n = len(ts)
    bins = 20
    ts_binned = np.digitize(ts, np.linspace(np.min(ts), np.max(ts), bins))
    mi = []
    for lag in range(1, max_lag):
        x = ts_binned[:-lag]
        y = ts_binned[lag:]
        hist_xy = np.histogram2d(x, y, bins=bins)[0]
        p_xy = hist_xy / np.sum(hist_xy)
        p_x = np.sum(p_xy, axis=1)
        p_y = np.sum(p_xy, axis=0)
        mi_val = 0
        for i in range(bins):
            for j in range(bins):
                if p_xy[i, j] > 0:
                    mi_val += p_xy[i, j] * np.log2(p_xy[i, j] / (p_x[i] * p_y[j]))
        mi.append(mi_val)
    mi = np.array(mi)
    for i in range(1, len(mi)-1):
        if mi[i] < mi[i-1] and mi[i] < mi[i+1]:
            return i + 1
    return 1

# Data Ingestion
data = ingest_telemetry("GPD/phases/04-production-execution-stability-profiling/production_results.bin")
ts = data[:, 0]
vorticity = data[:, 1]
tau = calculate_mutual_information(ts)
m = 3 # Confirmed dimension

# Embedding
X = np.array([[ts[i+j*tau] for j in range(m)] for i in range(len(ts)-m*tau)])
vort_mapped = vorticity[:len(X)]

# Poincaré Section
mean_plane = np.mean(X[:, 2])
z = X[:, 2]
# cut indices are for X[1:] where crossing occurs
indices = np.where((z[:-1] < mean_plane) & (z[1:] >= mean_plane))[0] + 1
cut = X[indices]

# Correlation Dimension
sample_X = X[::100]
tree = KDTree(sample_X)
r_min = np.min(tree.query(sample_X, k=2)[0][:,1])
r_max = np.max(np.std(sample_X, axis=0))
r_vals = np.logspace(np.log10(r_min), np.log10(r_max), 20)
C = [tree.count_neighbors(tree, r=r) / len(sample_X)**2 for r in r_vals]

# Serialization
np.savez('GPD/phases/05-statistical-analysis-reconstruction/topology_data.npz', 
         X=X[::100], vort=vort_mapped[::100], cut=cut, r_vals=r_vals, C=C)
print("[SUCCESS] Topology data serialized to topology_data.npz.")

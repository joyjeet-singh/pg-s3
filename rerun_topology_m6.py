{\rtf1\ansi\ansicpg1252\cocoartf2709
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # rerun_topology_m6.py\
# Re-estimates correlation dimension D2 with m=6 (Takens-compliant).\
# Run from the project2 root directory:\
#   python rerun_topology_m6.py\
\
import numpy as np\
import mmap\
import struct\
from scipy.spatial import KDTree\
\
# \uc0\u9472 \u9472  1. Ingest telemetry (same as execute_topology.py) \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \
def ingest_telemetry(file_path):\
    print(f"[INGEST] Reading \{file_path\} ...")\
    with open(file_path, "rb") as f:\
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)\
        magic, version, n_trajs, n_steps, dt, schema_id = struct.unpack(\
            "=4sIIQfI", mm[:28])\
        num_blocks = (mm.size() - 128) // 12\
        raw = np.frombuffer(mm, dtype=np.float32,\
                            offset=128, count=num_blocks * 3)\
        raw = raw.reshape(-1, 3).astype(np.float64)\
    print(f"[INGEST] Loaded \{len(raw)\} data points.")\
    return raw\
\
# \uc0\u9472 \u9472  2. Mutual information for tau (unchanged) \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \
def calculate_mutual_information(ts, max_lag=50):\
    bins = 20\
    ts_binned = np.digitize(ts, np.linspace(ts.min(), ts.max(), bins))\
    mi = []\
    for lag in range(1, max_lag):\
        x, y = ts_binned[:-lag], ts_binned[lag:]\
        hist_xy = np.histogram2d(x, y, bins=bins)[0]\
        p_xy = hist_xy / hist_xy.sum()\
        p_x  = p_xy.sum(axis=1)\
        p_y  = p_xy.sum(axis=0)\
        val  = 0.0\
        for i in range(bins):\
            for j in range(bins):\
                if p_xy[i, j] > 0:\
                    val += p_xy[i, j] * np.log2(\
                        p_xy[i, j] / (p_x[i] * p_y[j]))\
        mi.append(val)\
    mi = np.array(mi)\
    for i in range(1, len(mi) - 1):\
        if mi[i] < mi[i-1] and mi[i] < mi[i+1]:\
            return i + 1\
    return 1\
\
# \uc0\u9472 \u9472  3. Correlation dimension estimator \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \
def correlation_dimension(X, n_r=20):\
    sample = X[::100]           # subsample for speed\
    tree   = KDTree(sample)\
    r_min  = np.min(tree.query(sample, k=2)[0][:, 1])\
    r_max  = np.std(sample)\
    r_vals = np.logspace(np.log10(r_min), np.log10(r_max), n_r)\
    C = [tree.count_neighbors(tree, r=r) / len(sample)**2 for r in r_vals]\
    # log-log slope = D2\
    log_r = np.log(r_vals)\
    log_C = np.log(np.clip(C, 1e-12, None))\
    # fit on the middle 60% of the scaling range (avoid edge artefacts)\
    lo, hi = int(0.2 * n_r), int(0.8 * n_r)\
    slope  = np.polyfit(log_r[lo:hi], log_C[lo:hi], 1)[0]\
    return slope, r_vals, C\
\
# \uc0\u9472 \u9472  4. Main \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \
data = ingest_telemetry(\
    "GPD/phases/04-production-execution-stability-profiling/production_results.bin")\
ts = data[:, 0]\
\
tau = calculate_mutual_information(ts)\
print(f"[AMI]    Embedding delay  tau = \{tau\}")\
\
# KEY CHANGE: m=6 instead of m=3\
m = 6\
print(f"[EMBED]  Embedding dim    m   = \{m\}  (Takens requires m >= 2*D2+1)")\
\
n_embed = len(ts) - m * tau\
if n_embed <= 0:\
    raise ValueError(\
        f"Time series too short for m=\{m\}, tau=\{tau\}. "\
        f"Need at least \{m*tau+1\} points, have \{len(ts)\}.")\
\
X = np.array([[ts[i + j*tau] for j in range(m)] for i in range(n_embed)])\
print(f"[EMBED]  Attractor shape  \{X.shape\}")\
\
D2, r_vals, C = correlation_dimension(X)\
print(f"\\n[RESULT] Correlation dimension D2 = \{D2:.4f\}")\
print(f"[CHECK]  Takens condition: m=\{m\} >= 2*D2+1 = \{2*D2+1:.2f\}  "\
      f"\uc0\u8594   \{'SATISFIED' if m >= 2*D2+1 else 'VIOLATED \'97 increase m'\}")\
\
# \uc0\u9472 \u9472  5. Save updated topology data \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \
vorticity = data[:, 1]\
vort_mapped = vorticity[:n_embed]\
\
# Poincar\'e9 section\
mean_plane = np.mean(X[:, 2])\
z = X[:, 2]\
indices = np.where((z[:-1] < mean_plane) & (z[1:] >= mean_plane))[0] + 1\
cut = X[indices]\
\
out_path = "GPD/phases/05-statistical-analysis-reconstruction/topology_data_m6.npz"\
np.savez(out_path,\
         X=X[::100], vort=vort_mapped[::100],\
         cut=cut, r_vals=r_vals, C=C,\
         D2=D2, m=m, tau=tau)\
print(f"\\n[SAVED]  \{out_path\}")\
print("Done.")}
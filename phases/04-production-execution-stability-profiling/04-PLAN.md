---
phase: 04-production-execution-stability-profiling
plan: 01
type: execute
wave: 1
depends_on: [01, 02, 03]
files_modified:
  - GPD/phases/04-production-execution-stability-profiling/04-PLAN.md
  - GPD/STATE.md
  - GPD/ROADMAP.md
interactive: false

conventions:
  units: "natural"
  metric: "(-,+,+,+)"
  coordinates: "Cartesian"

contract:
  schema_version: 1
  scope:
    question: "How to execute massive multi-trajectory production runs with chaos injection while maintaining strict 5GB RSS and symplectic integrity?"
    in_scope:
      - "Multi-trajectory wavepacket initialization."
      - "Chaos injection and VPS-preserving perturbation."
      - "Real-time memory and energy drift monitoring."
      - "Zero-overhead binary telemetry serialization."
      - "Linear Response Check mandatory control benchmark."
    out_of_scope:
      - "Distributed cluster orchestration (single-node multi-core only)."
  context_intake:
    must_include_prior_outputs: ["GPD/phases/03-neural-physical-coupling/03-SUMMARY.md"]
    user_asserted_anchors: ["rss-ceiling-5gb", "buffer-ceiling-1gb"]
    known_good_baselines: ["Phase 03 ECE_max: 4.82e-08"]
  claims:
    - id: "c_production_stability"
      statement: "The execution framework maintains RSS < 5GB over 10^7 steps while preserving 4th-order VPS and detecting chaos divergence."
      deliverables: ["deliv-04-plan"]
      acceptance_tests: ["test-long-term-rss", "test-chaos-telemetry", "test-vps-persistence", "test-linear-response"]
  deliverables:
    - id: "deliv-04-plan"
      kind: "report"
      path: "GPD/phases/04-production-execution-stability-profiling/04-PLAN.md"
      description: "Comprehensive Phase 04 Execution Plan."
  acceptance_tests:
    - id: "test-long-term-rss"
      subject: "c_production_stability"
      kind: "benchmark"
      procedure: "Run 10^6 steps and monitor RSS via task_info/getrusage."
      pass_condition: "RSS < 5GB"
    - id: "test-chaos-telemetry"
      subject: "c_production_stability"
      kind: "consistency"
      procedure: "Inject perturbation and verify Lyapunov exponent calculation."
      pass_condition: "L > 0 detected in chaotic regime."
    - id: "test-vps-persistence"
      subject: "c_production_stability"
      kind: "symmetry"
      procedure: "Verify 4th-order VPS remains within 1e-8 during high-gradient forcing."
      pass_condition: "VPS < 1e-8"
    - id: "test-linear-response"
      subject: "c_production_stability"
      kind: "consistency"
      procedure: "Execute control impulse and verify deviation against Jacobian within 5%."
      pass_condition: "Linear response deviation < 5% error."
  forbidden_proxies: []
  uncertainty_markers:
    weakest_anchors: ["AVX2 register pressure in high-gradient forcing"]
    disconfirming_observations: ["Unexpected RSS spikes exceeding 4.8GB during multi-trajectory scaling"]
---

# Phase 04: Production Execution, Chaos Injection, and Long-Term Stability Profiling

## 1. Production Run Execution Framework

### 1.1 Multi-Trajectory Initialization
- **Localized Wavepacket Distribution:** Initialize trajectories using a Gaussian wavepacket in phase space: $\psi(q, p) \propto \exp(-\frac{(q-q_0)^2}{2\sigma_q^2} - \frac{(p-p_0)^2}{2\sigma_p^2})$.
- **Scaling Orchestration:** Parallel execution across CPU cores using OpenMP, where each thread manages a subset of the wavepacket ensemble to maximize L1/L2 cache locality.
- **Register Allocation:** Ensure $q$ and $p$ vectors are pinned to YMM registers during the integration inner loop to eliminate memory stalls.

### 1.2 Parameter Grid-Search Layout
- **Coupling Constants ($\alpha$):** Linear sweep $[0.0, 1.0]$ with $\delta\alpha = 0.05$.
- **Forcing Frequencies ($\omega$):** Logarithmic scale $[10^{-1}, 10^2]$ Hz to capture resonance overlaps.
- **Dissipation Scales ($\gamma$):** $[10^{-4}, 10^{-1}]$ to probe the transition from near-symplectic to strongly dissipative regimes.

### 1.3 Memory Tracking & RSS Management
- **Monitoring Loop:** Query `getrusage` (RSS) and `task_info` (Resident Size) every $10^4$ steps.
- **5GB RSS Guarantee:** Implement a 'soft-ceiling' at 4.5GB. Upon breach, trigger immediate decimation of the zero-copy buffer and flush non-essential telemetry.
- **Heap Fragmentation Control:** Use `aligned_alloc` for all SIMD vectors and avoid mid-run allocations/deallocations to prevent heap fragmentation.

## 2. Chaos Injection & Perturbation Engine

### 2.1 'chaos_injection.py' Execution Logic
- **Discrete Perturbations:** Inject bounded shifts $\delta p \sim \mathcal{U}(-\epsilon, \epsilon)$ into the momentum field at periodic intervals $T_{inj}$.
- **Field-Wise Injection:** Perturbations must be spatially correlated to maintain the VPS condition, using a localized kernel $\exp(-|x-x_c|^2/\sigma^2)$.

### 2.2 High-Gradient VPS Preservation
- **4th-Order VPS Stencil:** Maintain the 13-point stencil for vorticity preservation.
- **Adaptive Damping:** Under high-gradient forcing ($|\nabla \omega| > \theta$), apply a local low-pass filter to the velocity field before the projection layer to prevent VPS blow-up.
- **Branchless Logic:** Use `_mm256_blendv_ps` to apply damping based on gradient magnitude without breaking the SIMD pipeline.

### 2.3 On-the-Fly Telemetry
- **Divergence Rates:** Calculate $\delta(t) = |x_1(t) - x_2(t)|$ for twin-trajectory pairs.
- **Linear Response Check (Mandatory Control):** Every $10^5$ steps, execute a control benchmark where a small, known impulse $\delta p$ is injected. The resulting trajectory deviation must match the linear response approximation $J(t) \delta p$ within a $5\%$ tolerance. This serves as the grounding anchor for the predictability horizon study.
- **Lyapunov Exponent ($\lambda$):** Compute $\lambda = \frac{1}{t-t_0} \ln \frac{\delta(t)}{\delta(t_0)}$ at decimation checkpoints.

## 3. Telemetry, Logging & Decimation Strategy

### 3.1 High-Throughput Logging Pipeline
- **Zero-Copy Streamer:** Utilize the 1GB buffer established in Phase 03. Data is memory-mapped directly from the AVX2 kernel output.
- **AVX2 Pinning (Environment Constraint):** Force `OV_CPU_DISPATCH_ARCH=AVX2` and `OPENVINO_CPU_EXTENSION_LIST=avx2` to bypass AVX-512 frequency scaling penalties and maintain deterministic 256-bit register saturation.
- **Adaptive Decimation:** When the 1GB buffer reaches 90% capacity, increase the sampling stride $S$ by a factor of 2.
- **Pre-Decimation LPF:** Apply a 3-tap moving average filter ($\alpha=0.25$) to state variables to eliminate high-frequency noise before downsampling.

### 3.2 Binary Schema (Unpadded Float Arrays)
- **Header (128 bytes):** `[Magic (4)][Version (4)][N_Trajectories (4)][N_Steps (8)][Dt (4)][Schema_ID (4)][Padding...]`
- **Data Block:** Row-major $N \times D$ float32 arrays, where $D$ includes $\{q_i, p_i, \Delta E, \omega, \lambda\}$.
- **Alignment:** All data blocks aligned to 64-byte boundaries to match L3 cache line widths.

## 4. Automated Failure Modes & Interventions (Fail-Fast Logic)

### 4.1 Termination Thresholds
- **Energy Drift Bound:** Abort if $|\frac{d(\Delta E)}{dt}| > 10^{-7} \cdot E_0$ over a $10^3$ step window (where $E_0$ is the initial system energy). This tighter bound addresses Phase 03 floating-point drift concerns.
- **Structural Collapse:** Immediate abort if `isnan(q)` or `isinf(p)` is detected via AVX2 `_mm256_cmp_ps_ph` check.
- **Linear Response Violation:** Abort if $\delta(t)$ exceeds $10^2 \times \delta(0)$ in a regime where linear response is analytically guaranteed.

### 4.2 Checkpointing & Recovery
- **Safe-State Serialization:** Write full register state (YMM0-YMM15) and memory-mapped pointers to `.chk` file every $10^6$ steps.
- **Mid-Run Recovery:** Reload `.chk` to resume execution with bit-exact reproducibility.

## 5. Phase 04 Verification Checklist

| Metric | Target Value | Verification Method |
|--------|--------------|---------------------|
| Peak RSS | < 5.0 GB | `getrusage` Telemetry |
| Buffer Usage | < 1.0 GB | Streamer Watermark |
| Max ΔE Drift | < 1e-7 · E0 / 24h | Binary Output Analysis |
| VPS Residual | < 1e-9 | 4th-Order Stencil Check |
| Throughput | > 10^6 steps/sec | Wall-clock Timer |
| Disk I/O | < 50 MB/s | `iostat` / `iotop` |
| Chaos Detection | $\lambda$ accuracy > 95% | Benchmark vs. Lorenz System |
| Linear Response | Error < 5% | Control Impulse Benchmark |

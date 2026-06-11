# Roadmap: Physically-Grounded Selective State Space (PG-S3) Models

## Overview

This project aims to bridge the gap between high-efficiency linear-time sequence models (SSMs) and physically-consistent world modeling. By replacing standard Zero-Order Hold (ZOH) discretization with Symplectic Integrators and enforcing Hamiltonian latent dynamics, we develop PG-S3—a model that achieves $O(L)$ complexity while preserving the physical integrity (energy, momentum, spectral fidelity) of the modeled systems. The project targets CPU-bound environments using INT4 quantization and SIMD-optimized kernels.

## Contract Overview

| Contract Item | Advanced By Phase(s) | Status |
| ------------- | -------------------- | ------ |
| O(L) Complexity Verification | Phase 01 | Completed |
| Symplectic Dynamics Derivation | Phase 02 | Completed |
| SIMD Associative Scan Kernels | Phase 03 | Completed |
| Spectral Fidelity (Kolmogorov) | Phase 05 | Planned |
| Hamiltonian Conservation Proof | Phase 02, Phase 05 | Planned |
| Long-term Stability | Phase 04 | Planned |

## Phases

- [x] **Phase 01: Complexity Analysis & Benchmarking** - $O(L)$ verification and initial performance baselines.
- [x] **Phase 02: Implementation of Symplectic Selective Dynamics** - Formulation and coding of the Hamiltonian latent flow.
- [x] **Phase 03: Hardware Kernel Optimization** - SIMD (AVX-512/NEON) and mixed-precision optimization.
- [ ] **Phase 04: Production Execution, Chaos Injection, and Long-Term Stability Profiling** - Massive multi-trajectory scaling and chaos injection.
- [ ] **Phase 05: Final Validation & Paper Refinement** - Multi-environment benchmarking and result synthesis.

## Phase Details

### Phase 01: Complexity Analysis & Benchmarking

**Goal:** Establish the $O(L)$ complexity execution via branchless SIMD on CPU & SAQ INT4 Memory Architecture Grounding.
**Depends on:** None
**Requirements:** CALC-01, VAL-03
**Contract Coverage:**
- Advances: Hardware-specific O(L) complexity verification
- Deliverables: Complexity analysis, C++ SIMD Kernel Blueprint, OpenVINO-compatible Memory Allocation Map, Benchmarking report.
- Anchor coverage: AVX2/AVX-512 register saturation, <5GB memory allocation.
- Forbidden proxies: Ignoring L3 cache spilling or memory allocation limits.
**Success Criteria:**

1. Model achieves true $O(L)$ execution via branchless SIMD on CPU.
2. Memory footprint is confirmed < 5GB with zero L3 cache spilling.
3. OpenVINO integration pathway validated.

Plans:
- [x] 01-01: Derivation of parallel prefix sum costs on SIMD hardware.
- [x] 01-02: Initial red-team probe of Rate-Distortion bounds for INT4.
- [x] 01-GAP: Implementation of hardware-rigorous SIMD kernels and INT4 SAQ.

---

### Phase 02: Implementation of Symplectic Selective Dynamics

**Goal:** Formulate and implement the symplectic latent update rule to ensure energy conservation.
**Depends on:** Phase 01
**Requirements:** FORM-01, FORM-02, CALC-02
**Contract Coverage:**
- Advances: Symplectic Dynamics Derivation, Hamiltonian Conservation Proof
- Deliverables: Symplectic update code, Energy conservation proof.
- Anchor coverage: Störmer-Verlet integration, Hamiltonian $\mathcal{H}(q,p)$.
- Forbidden proxies: Using standard ZOH discretization.
**Success Criteria:**

1. Störmer-Verlet update rule is correctly integrated into the selection mechanism.
2. Latent state $h = [q, p]^T$ preserves the Hamiltonian $\mathcal{H}$ in the limit of small $\Delta$.
3. Latent CFL condition is derived and coupled to the selection parameter $\Delta$.

Plans:
- [x] 02-01: Mathematical derivation of the Symplectic Selective SSM update.
- [x] 02-02: Implementation of the Störmer-Verlet latent kernel.
- [x] 02-03: Derivation and integration of the Latent CFL stability condition.

---

### Phase 03: Hardware Kernel Optimization

**Goal:** Optimize the associative scan and memory access patterns for target CPU architectures.
**Depends on:** Phase 01, Phase 02
**Requirements:** NUM-01, NUM-02
**Contract Coverage:**
- Advances: SIMD Associative Scan Kernels
- Deliverables: AVX-512 and ARM NEON kernels, Mixed-precision update module.
- Anchor coverage: Branchless SIMD swizzling, Pinned memory buffers.
- Forbidden proxies: Unoptimized recursive scan.
**Success Criteria:**

1. SIMD-optimized associative scan achieves $>2\times$ speedup over naive C++ implementation.
2. Mixed-precision (INT4/BF16) stability is maintained during long sequence rollouts.
3. Cache-local tiling ($T=64$ for x86, $T=16$ for ARM) is implemented and verified.

Plans:
- [x] 03-01: AVX-512/ARM NEON branchless scan implementation.
- [x] 03-02: Mixed-precision buffer management and pinned memory integration.
- [x] 03-03: Hardware-specific tile size optimization.

---

### Phase 04: Production Execution, Chaos Injection, and Long-Term Stability Profiling

**Goal:** Execute full-scale production runs with discrete perturbations and stability monitoring.
**Depends on:** Phase 02, Phase 03
**Requirements:** EXEC-01, EXEC-02
**Contract Coverage:**
- Advances: Predictability Horizon (L_crit), Long-term stability
- Deliverables: 04-PLAN.md, chaos_injection.py (updated), production results.
- Anchor coverage: RSS < 5GB, Buffer < 1GB, 4th-order VPS.
- Forbidden proxies: Memory leaking beyond 5GB ceiling.
**Success Criteria:**

1. Production runs maintain RSS < 5GB over 10^7 steps.
2. Chaos injection correctly triggers Lyapunov exponent telemetry.
3. Automatic abort triggers prevent non-physical divergence.

Plans:
- [ ] 04-01: Implementation of multi-trajectory wavepacket scaling and monitoring.
- [ ] 04-02: Integration of chaos_injection.py with VPS-preserving logic.

---

### Phase 05: Final Validation & Paper Refinement

**Goal:** Validate the full PG-S3 model across rigid-body and fluid environments and synthesize results.
**Depends on:** Phase 04
**Requirements:** VAL-01, VAL-02
**Contract Coverage:**
- Advances: Spectral Fidelity, Hamiltonian Conservation Proof, Predictability Horizon
- Deliverables: Final benchmark report, Paper draft/Refinement.
- Anchor coverage: MuJoCo, Navier-Stokes, $L_{crit}$ metrics.
**Success Criteria:**

1. PG-S3 outperforms standard Mamba/SSM in Hamiltonian conservation by $>10\times$.
2. Predictability horizon $L_{crit}$ is extended by $>30\%$ compared to non-symplectic models.
3. Spectral fidelity in Navier-Stokes environments matches ground-truth Kolmogorov scales.

Plans:
- [ ] 05-01: Production runs on MuJoCo and Navier-Stokes.
- [ ] 05-02: Calculation of $L_{crit}$ and energy error metrics.
- [ ] 05-03: Synthesis of results into the final research document.

## Progress

**Execution Order:**
1 -> 2 -> 3 -> 4 -> 5

| Phase                                  | Plans Complete | Status      | Completed |
| -------------------------------------- | -------------- | ----------- | --------- |
| 01. Complexity Analysis & Benchmarking | 3/3            | Complete    | 2026-06-05  |
| 02. Implementation of Symplectic       | 3/3            | Complete    | 2026-06-07  |
| 03. Hardware Kernel Optimization       | 3/3            | Complete    | 2026-06-08  |
| 04. Production Execution & Stability   | 2/2            | Complete    | 2026-06-08  |
| 05. Statistical Analysis & Reconstruction| 0/3            | In Progress | -         |

## Risk Register

| Phase | Top Risk | Probability | Impact | Mitigation |
|-------|---------|:-:|:-:|-----------|
| 02 | Symplectic drift due to selection noise | MEDIUM | HIGH | Monitor Hamiltonian residual; implement refinement step if drift > threshold |
| 03 | AVX-512 register pressure stalling pipe | MEDIUM | MEDIUM | Profile with VTune; adjust tiling size $T$ dynamically |
| 04 | Memory allocation exceeding 5GB ceiling | HIGH | HIGH | Real-time monitoring with soft-ceiling at 4.5GB |
| 05 | Numerical instability in stiff N-S flows | LOW | HIGH | Latent CFL condition must be strictly enforced |

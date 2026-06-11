# Phase 03: Neural-Physical Coupling - RESEARCH.md

## User Constraints

See phase `03-CONTEXT.md` for locked decisions and user constraints that apply to this phase.

Key constraints affecting this research:
- **Coupling Strategy:** Implement hybrid projection (direct AVX2-optimized projection + periodic threshold-triggered stabilization).
- **Performance:** AVX2-optimized projection layers, zero-copy data streaming.
- **Resource Constraints:** Memory RSS < 5GB, Buffer < 1GB.
- **Stability Metrics:** $\Delta E$ (energy violation) stability; $L_{crit}$ predictability horizon.
- **Discretion:** AVX2 intrinsic implementation, low-pass filter design, and linear response benchmark implementation.

## Active Anchor References

- **Stability plots from Phase 02**
  - Why it matters: Defines the expected baseline energy behavior and stability regime of the symplectic core.
  - Required action: Use these plots as the primary reference to validate that coupling does not break symplectic integrity.
- **Project Requirements (NUM-01, NUM-02)**
  - Why it matters: Specifies requirements for SIMD-optimized associative scan kernels (AVX2 focus, extensible to AVX-512/NEON) and mixed-precision (INT4/BF16) recurrent updates.

## Mathematical Framework

- **Hybrid Projection:**
  - Let $x_t \in \mathbb{R}^n$ be the latent state from the symplectic core.
  - Projection operator $\Pi: \mathbb{R}^n \rightarrow \mathcal{M}$ (where $\mathcal{M}$ is the physical manifold).
  - Stabilization $\mathcal{S}(\tilde{x}_t)$: Threshold-triggered, dissipative correction applied when $\text{dist}(\Pi(x_t), x_{physical}) > \tau$.
- **Spectral Regularization:** Captures Kolmogorov energy cascades in the latent state (required for physical fidelity).
- **Dynamic Sampling:** Low-pass filtering followed by downsampling to manage temporal resolution without aliasing.

## Standard Approaches

- **Zero-Copy Streaming:** Use `mmap` with `MAP_SHARED` for inter-process communication or `pinned` (locked) memory buffers in C++ (`mlock`) to avoid OS-level copying overhead.
- **Mixed-Precision Updates:** Utilize hardware-specific support (e.g., AVX2 intrinsics for BF16, or quantized INT4 operations) to reduce memory bandwidth requirements.
- **Low-Pass Filtering:** FIR (Finite Impulse Response) or IIR (Infinite Impulse Response) filters; FIR is preferred for guaranteed stability in physical systems.

## Existing Results to Leverage

- **Symplectic Shadow Hamiltonian:** The core dynamics (Phase 02) already satisfies a shadow Hamiltonian; the projection must respect this as much as possible.
- **AVX2 Intrinsic Patterns:** Leverage standard vectorization for associative operations (prefix sums, dot products) used in projection.

## Don't Re-Derive

- Standard Hamiltonian mechanics (Phase 02).
- Basic properties of the Störmer-Verlet integrator (Phase 02).
- The fundamental definitions of SIMD associative scans (well-established).

## Computational Tools

- **AVX2 Intrinsics:** Use `immintrin.h` for SIMD operations.
- **Memory Management:** `mmap` / `munmap` for streaming, `posix_memalign` for aligned buffers, `mlock` for pinning memory.
- **Implementation:** C++ (for core throughput), potentially wrapped by Python for data-stream orchestrator.
- **Mixed-Precision:** Consider using specialized libraries (like Eigen or OpenVINO custom kernels) for efficient INT4/BF16 arithmetic.

## Validation Strategies

- **$\Delta E$ Stability:** Track $|\mathcal{H}(x_{coupled}) - \mathcal{H}(x_{core})|$ and compare against Phase 02 stability plots.
- **Physical Fidelity:** Ensure dissipative projection bound $\langle F, p \rangle \le 0$ holds.
- **$L_{crit}$ Check:** Measure predictability horizon using local wavepacket propagation.
- **Memory/Latency:** Profile using `perf` and custom instrumentation to ensure constraints are met.

## Common Pitfalls

- **Spurious Energy Injection:** Threshold-triggered stabilization might inject energy if not implemented as a strictly dissipative process.
- **Aliasing:** Insufficient low-pass filtering before sampling rate reduction will alias high-frequency noise into the physics-informed latent state.
- **Memory Bandwidth Bottleneck:** Even if total memory is low, high-frequency access to unoptimized buffers will cause throughput bottlenecks.

## Key Equations and Starting Points

- **Dissipative Projection Bound:** $\langle F, p \rangle \le 0$ (must be enforced).
- **Threshold Condition:** $\|\tilde{x}_t - x_{physical}\| > \tau$ (trigger for stabilization).
- **Low-Pass Filter:** $y[n] = \sum_{k=0}^N b_k x[n-k]$.

### Package / Framework Reuse Decision

- **Bespoke implementation** is required for the zero-copy streamer and AVX2-optimized projection layers to ensure compliance with the strict memory (<5GB) and buffer (<1GB) constraints and to integrate the threshold-triggered stabilization directly with the core symplectic dynamics.

## Caveats and Alternatives

- **Self-Critique:** Hybrid projection might be sensitive to the stabilization threshold $\tau$. If $\tau$ is too small, excessive stabilization; if too large, physical drift becomes irreversible.
- **Alternative:** Fully continuous dissipative projection (e.g., stochastic damping) might be more stable but harder to implement with the current symplectic core.

## Sources

- Numerical Integration of Hamiltonian Systems (Hairer, Lubich, Wanner).
- AVX2 Instruction Set Reference (Intel).
- Literature on Symplectic Integrators and Dissipative Systems.

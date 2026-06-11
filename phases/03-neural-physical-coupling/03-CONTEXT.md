# Phase 03: Neural-Physical Coupling - Context

**Gathered:** 2026-06-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Bridge the bare-metal symplectic core (from Phase 02) with physical datasets via AVX2-optimized projection layers and high-throughput zero-copy streaming, satisfying strict memory and latency constraints.

</domain>

<contract_coverage>
## Contract Coverage

- [Claim-coupling]: Satisfy memory ceiling (<5GB), buffer limits (<1GB), and AVX2 performance targets.
- [Acceptance signal]: Memory RSS < 5GB, Buffer < 1GB, AVX2 utilization benchmark, $\Delta E$ stability.
- [False progress to reject]: Non-physical dynamics in projection, hidden dissipation violation, throughput bottlenecks.
</contract_coverage>

<user_guidance>
## User Guidance To Preserve

- **User-stated observables:** $\Delta E$ (energy violation), Predictability horizon $L_{crit}$.
- **User-stated deliverables:** AVX2 projection layers, zero-copy data streamer.
- **Must-have references / prior outputs:** Stability plots from Phase 02.
- **Stop / rethink conditions:** Drift in $\Delta E$ exceeds benchmark, memory ceiling approaching 4.5GB.
</user_guidance>

<decisions>
## Methodological Decisions

### Shear Decomposition
- **Strategy:** Direct AVX2 ordering for performance.
- **Drift:** Ignore symplecticity drift if it stays within machine epsilon thresholds.
- **Decisive Observable:** Energy violation $\Delta E$.
- **Failure Signal:** Sudden growth in $\Delta E$.
- **Anchor:** Phase 02 stability plots.

### Dissipative Projection
- **Strategy:** Hybrid projection (direct projection with periodic stabilization).
- **Stabilization:** Threshold-triggered stabilization.
- **Justification:** Dynamic symplectic correction.
- **False Progress:** Non-physical dynamics.

### Memory Constraints
- **Strategy:** Dynamic sampling rate reduction (for temporal consistency).
- **Aliasing Mitigation:** Low-pass filtering before reducing rate.

### Predictability Horizon ($L_{crit}$)
- **Method:** Localized wavepackets (as local stability probe).
- **Failure Condition:** Deviation > $\epsilon$ from benchmark.
- **Control Experiment:** Linear response check.

### Agent's Discretion
- Library choice for AVX2 intrinsics implementation.
- Specific low-pass filter design.
- Implementation of linear response benchmark.
</decisions>

<assumptions>
## Physical Assumptions
- AVX2 ordering stability is sufficient: Direct ordering maintains drift within epsilon | Symplecticity of the core dynamics is compromised.
- Strong dissipative forcing regime is applicable: Threshold-triggered correction handles forcing peaks | Inaccurate dissipation projection.
</assumptions>

<limiting_cases>
## Expected Limiting Behaviors
- High-coupling limit: Hybrid projection must maintain dissipation bound $\langle F, p \rangle \le 0$.
- Low-forcing regime: Drift in $\Delta E$ should remain minimal.
</limiting_cases>

<anchor_registry>
## Active Anchor Registry

- Stability plots from Phase 02
  - Why it matters: Constrains the symplectic core interface.
  - Carry forward: planning, execution, verification.
  - Required action: use, compare.

</anchor_registry>

<skeptical_review>
## Skeptical Review

- **Weakest anchor:** Direct AVX2 ordering stability in high-coupling dissipative regimes.
- **Unvalidated assumptions:** Threshold-triggered stabilization handles strong dissipative forcing accurately.
- **Competing explanation:** $\Delta E$ growth could be numerical rather than physical.
- **Disconfirming check:** Sudden $\Delta E$ growth in weak-forcing regime.
- **False progress to reject:** High performance/low memory usage but non-physical trajectory.
</skeptical_review>

<deferred>
## Deferred Ideas

- Higher-order dissipation projection — future phase
- Non-Cartesian coordinate support — future phase
</deferred>

---
_Phase: 03-neural-physical-coupling_
_Context gathered: 2026-06-07_

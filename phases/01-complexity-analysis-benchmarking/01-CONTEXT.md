# Phase 1: Complexity Analysis & Benchmarking - Context

**Gathered:** 2026-05-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish theoretical foundations and empirical baseline performance for 4 candidate attention mechanisms.

Requirements: [THEO-01, BENCH-01]
</domain>

<contract_coverage>
## Contract Coverage

- Claim / deliverable: Theoretical complexity bounds and empirical scaling curves.
- Acceptance signal: Identify the optimal physical regime and benchmark performance vs SDPA.
- False progress to reject: Naive attention implementations, synthetic-data-only benchmarks.
</contract_coverage>

<user_guidance>
## User Guidance To Preserve

- **User-stated observables:** Wall-clock time (sec), peak RAM (RSS), perplexity degradation (%).
- **User-stated deliverables:** Scaling plots (n vs time, n vs RAM), complexity derivation report, benchmark log.
- **Must-have references / prior outputs:** PyTorch `nn.MultiheadAttention` as baseline.
- **Stop / rethink conditions:** If no candidate achieves >2x speedup or perplexity degradation >5%.
</user_guidance>

<decisions>
## Methodological Decisions

### Approximation Formalism

- Linear Attention (Performer) prioritized due to FAVOR+ grounding.
- Orthogonal Random Features for variance reduction.
- $r=256$ fixed as constant.
- Crossover at $n \le 128$: standard SDPA; $n > 128$: FAVOR+ Performer.

### Baseline Definition

- Implementation: `torch.nn.functional.sdpa`
- Optimization: FlashAttention enabled.
- Measurement Scope: Full attention block (including projections).
- Compilation: `torch.compile` enabled.

### CPU Benchmarking Protocol

- Warm-up: 20 forward passes (n=256), 2s wait.
- Timer: `torch.utils.benchmark.Timer` (5s, 50 reps).
- Interleaving: Alternate SDPA and Performer runs.
- Metrics: Median latency, speedup ratio (t_SDPA / t_approx).
- RAM: Peak RSS tracker.
- Robustness: Report crossover range if noise is significant.
</decisions>

<assumptions>
## Physical Assumptions

- FAVOR+ variance bound holds for trained models (attention sparsity assumption). | Breaks if attention is not sparse.
- CPU thermal state impacts implementations uniformly. | Breaks if implementations have wildly different instruction-cache/memory-bus utilization.
</assumptions>

<limiting_cases>
## Expected Limiting Behaviors

- $n \le 128$: SDPA should consistently outperform.
- $n > 128$: Linear attention (FAVOR+) should show $O(n)$ speedup vs $O(n^2)$.
</limiting_cases>

<anchor_registry>
## Active Anchor Registry

- PyTorch SDPA (torch.nn.functional.scaled_dot_product_attention)
  - Why it matters: Authoritative baseline for performance.
  - Carry forward: planning, execution, verification.
  - Required action: read, use, cite.

</anchor_registry>

<skeptical_review>
## Skeptical Review

- **Weakest anchor:** Empirically determined crossover point (noise sensitive).
- **Unvalidated assumptions:** Orthogonal features deliver the predicted variance reduction on the specific CPU architecture.
- **Competing explanation:** Speedups might be due to FlashAttention/compilation overhead differences rather than algorithmic complexity.
- **Disconfirming check:** Failure of FAVOR+ to show $O(n)$ scaling vs SDPA $O(n^2)$ beyond $n=512$.
- **False progress to reject:** Benchmark speedups that are statistically noisy or not reproducible under thermal-steady-state.
</skeptical_review>

<deferred>
## Deferred Ideas

- Full training loop benchmarking (Phase 2).
- Ablation studies (Phase 3).
</deferred>

---

_Phase: 01-complexity-analysis-benchmarking_
_Context gathered: 2026-05-31_

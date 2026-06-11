# Research: Complexity Analysis & Benchmarking

## User Constraints

See phase `01-complexity-analysis-benchmarking/01-CONTEXT.md` for locked decisions and user constraints that apply to this phase.

Key constraints affecting this research:
- **Locked Methods:** Linear Attention (Performer/FAVOR+ with $r=256$), Sliding Window, SVD-based low-rank, and SSM are the four candidates.
- **Baseline:** `torch.nn.functional.sdpa` with `torch.compile` is the required baseline.
- **Environment:** CPU-only (Intel i5, 8GB RAM).
- **Deliverables:** Scaling plots (n vs time, n vs RAM), complexity derivation report, benchmark log.
- **Acceptance:** Must achieve >2x speedup on CPU for $n=512$, with <5% perplexity degradation.
- **Discretion:** While the methodology is largely locked, the choice of specific implementations for the four candidate attention mechanisms is left to researcher discretion, provided they fit the CPU constraints.

## Active Anchor References

- [PyTorch SDPA (`torch.nn.functional.scaled_dot_product_attention`)](https://pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html)
  - This is the mandatory baseline. All performance comparisons must be relative to this, using the specified CPU benchmarking protocol.

## Mathematical Framework

The goal is to move from $O(n^2 \cdot d)$ complexity to $O(n \cdot d \cdot \text{factor})$ where $\text{factor} \ll n$.

- **Standard Attention:** $Softmax(\frac{QK^T}{\sqrt{d}})V$. Complexity $O(n^2d + n^2d) = O(n^2d)$.
- **Linear Attention (FAVOR+):** Approximate $Softmax(QK^T) \approx \phi(Q)\phi(K)^T$ using random features $\phi$. Complexity $O(ndr)$ where $r$ is the number of random features.
- **Sliding Window:** Localized attention mask. Complexity $O(ndw)$ where $w$ is the window size.
- **Low-Rank:** $QK^T \approx UV^T$. Complexity $O(ndk)$ where $k$ is the rank.
- **SSM:** $h_t = Ah_{t-1} + Bx_t$. Complexity $O(nd^2)$ per step, $O(n)$ total.

## Standard Approaches

- **Linear Attention:** Use Orthogonal Random Features (ORF) for variance reduction. $r=256$ is fixed.
- **Benchmarking Protocol:** `torch.utils.benchmark.Timer` is the standard tool. Must adhere strictly to the 20 warm-up passes and 50 reps/5s constraint.

## Existing Results to Leverage

- [Choromanski et al. (2020), "Rethinking Attention with Performers"](): Validates FAVOR+ approach and the use of ORF for variance reduction.
- Performance characteristics of `torch.compile` on CPU, which can significantly optimize tensor contraction patterns.

## Don't Re-Derive

- Do not re-derive the theoretical $O(n^2)$ complexity of standard attention.
- Do not re-derive the mathematical convergence of random Fourier features (standard literature result).

## Computational Tools

- **Primary Framework:** PyTorch (for both baseline and implementation of candidates).
- **Compilation:** `torch.compile` (mandatory for baseline).
- **Profiling:** `torch.utils.benchmark` for latency, `psutil` or `memory_profiler` for peak RSS (as required by user constraints).

### Package / Framework Reuse Decision

- **Baseline:** Reuse `torch.nn.functional.sdpa` directly.
- **Candidate Implementations:**
  - **Linear Attention:** Implement based on FAVOR+ (can use lightweight custom module).
  - **Sliding Window:** Use `torch.nn.functional.scaled_dot_product_attention` with a causal/local mask (efficient implementation available in modern PyTorch).
  - **Low-Rank:** Bespoke implementation of low-rank projection for $Q$ and $K$.
  - **SSM:** Use a standard library if possible (e.g., `mamba-ssm` or lightweight Mamba implementation), or a simplified recurrent state space implementation. If dependencies are too heavy, a bespoke PyTorch implementation of a linear SSM is required.

## Validation Strategies

- **Perplexity Check:** Evaluate on held-out corpus (as specified in contract) to ensure <5% degradation.
- **Symmetry Checks:** Ensure causal masks are correctly applied where required.
- **Thermal Steady State:** The 20 warm-up passes are crucial to ensure CPU frequency stability.
- **Crossover Point:** Statistically validate the $n=128$ crossover using standard error on the 50 repetitions.

## Common Pitfalls

- **Memory Bandwidth Bottleneck:** On CPU, performance is often limited by memory bandwidth, not just FLOPs. Complex attention mechanisms might perform fewer operations but have worse cache locality than SDPA.
- **Noise in Benchmarking:** CPU background processes can drastically affect timing. Ensure minimal environment activity.
- **Incorrect Masking:** Using a global mask when a local/causal mask is expected in Sliding Window.
- **Thermal Throttling:** Prolonged benchmarking on a laptop CPU can induce thermal throttling, invalidating measurements.

## Key Equations and Starting Points

- **Linear Attention:** $Attention(Q, K, V) = \frac{\phi(Q)(\phi(K)^T V)}{\phi(Q)1^T}$
- **Benchmark:** `timer = torch.utils.benchmark.Timer(stmt="func()", setup="...")`

## Caveats and Alternatives

- **Adversarial Self-Critique:**
  - The $n=128$ crossover point may be highly specific to the Intel i5 architecture.
  - The 8GB RAM limit is tight; if the candidate implementations (like SSM) require large state storage, we may exceed this.
  - Linear attention (FAVOR+) can show significant perplexity degradation if $r=256$ is not sufficient for the target model.
- **Alternatives:** If FAVOR+ shows >5% degradation, consider increasing $r$ (though this increases memory/time) or switching to a different approximation (e.g., Kernel-based).

## Sources

- [Choromanski et al., "Rethinking Attention with Performers"]()
- [PyTorch Documentation (SDPA)](https://pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html)
- [Project Contract / Context provided in phase definition]

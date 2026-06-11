---
phase: 01-complexity-analysis-benchmarking
plan: 01-GAP
type: execute
wave: 2
depends_on: []
files_modified: [GPD/phases/01-complexity-analysis-benchmarking/benchmark_runner.py, GPD/phases/01-complexity-analysis-benchmarking/results.json]
interactive: false
gap_closure: true

tool_requirements:
  - id: "cpp-compiler"
    tool: "command"
    command: "g++ --version"
    purpose: "Compile C++ SIMD extensions (AVX2/AVX-512)"
    required: true

conventions:
  units: "natural"
  metric: "diag(-1,1,1,1)"
  coordinates: "Cartesian"
  fourier_convention: "physics (exp(-iwt))"

approximations:
  - name: "FAVOR+ Performer Orthogonal Random Features"
    parameter: "Number of features r=256"
    validity: "Approximates Gaussian kernel with variance reduction"
    breaks_when: "Attention pattern is highly dense/non-sparse"
    check: "SQNR monitoring of attention kernel approximation"

contract:
  schema_version: 1
  scope:
    question: "How can we achieve O(N) complexity and physical grounding in Performer/FAVOR+ World Models for CPU-bound environments?"
    in_scope: 
      - "Implement bare-metal SIMD FAVOR+ kernels (AVX2/AVX-512) with r=256"
      - "Verify benchmarking protocol: 20 warm-ups (n=256), Timer(5s, 50 reps), Metrics: Median Latency, Speedup Ratio, Peak RSS"
      - "Measure hardware-rigorous O(N) scaling within 8GB RAM budget"
  context_intake:
    must_include_prior_outputs: ["GPD/STATE.md", "GPD/phases/01-complexity-analysis-benchmarking/01-SUMMARY.md"]
    user_asserted_anchors: ["target-8GB-RAM"]
  claims:
    - id: "claim-linear-scaling-hardware"
      statement: "SIMD-optimized FAVOR+ Performer kernels (r=256) achieve linear O(N) scaling on CPU within the 8GB RAM constraint using the locked protocol."
      deliverables: ["deliv-simd-kernels", "deliv-benchmark-results"]
      acceptance_tests: ["test-linear-scaling", "test-memory-budget"]
  deliverables:
    - id: "deliv-simd-kernels"
      kind: "code"
      path: "GPD/phases/01-complexity-analysis-benchmarking/benchmark_runner.py"
      description: "C++-backed Performer FAVOR+ kernels (r=256) with AVX SIMD and INT4 SAQ."
    - id: "deliv-benchmark-results"
      kind: "data"
      path: "GPD/phases/01-complexity-analysis-benchmarking/results.json"
      description: "Hardware-rigorous latency and memory metrics matching the locked protocol."
  references:
    - id: "ref-hw-constraints"
      kind: "spec"
      locator: "Phase 01 Objective: Hardware Constraints"
      role: "must_consider"
      why_it_matters: "Defines the 8GB RAM and SIMD requirements."
      applies_to: ["claim-linear-scaling-hardware"]
      must_surface: true
      required_actions: ["use"]
  acceptance_tests:
    - id: "test-linear-scaling"
      subject: "claim-linear-scaling-hardware"
      kind: "benchmark"
      procedure: "Run benchmarking using 20 warm-ups (n=256) followed by 5s/50-rep Timer. Calculate Median Latency and Speedup Ratio for N=128 to 16384."
      pass_condition: "Execution time scales as O(N) with R^2 > 0.99; SDPA speedup ratio > 1."
      evidence_required: ["deliv-benchmark-results"]
    - id: "test-memory-budget"
      subject: "claim-linear-scaling-hardware"
      kind: "benchmark"
      procedure: "RSS monitoring during long-sequence runs (n=256)."
      pass_condition: "Peak RSS < 5GB (user budget for model/cache)."
      evidence_required: ["deliv-benchmark-results"]
  forbidden_proxies:
    - id: "fp-python-loops"
      subject: "claim-linear-scaling-hardware"
      proxy: "Measuring performance of Python-level recursive loops."
      reason: "Performer performance on CPU requires vectorized SIMD execution."
  uncertainty_markers:
    weakest_anchors: ["INT4 stability without full training loop"]
    disconfirming_observations: ["Memory spikes during forward pass exceeding budget"]
---

<objective>
Implement hardware-rigorous SIMD kernels for Performer FAVOR+ (r=256) and INT4 memory management to fix the placeholder benchmark runner and validate O(N) scaling on CPU within an 8GB RAM budget, in alignment with locked methodological decisions and the exact benchmarking protocol.

Purpose: Close the gap from Phase 01 where synthetic benchmarks failed.
Output: Vectorized Performer kernels, memory-optimized INT4 layout, O(N) validation data, and protocol-compliant benchmarking results.
</objective>

<tasks>
<task type="auto">
  <name>Task 1: Bare-Metal SIMD Performer FAVOR+ Kernels (r=256)</name>
  <files>GPD/phases/01-complexity-analysis-benchmarking/benchmark_runner.py</files>
  <action>Implement C++ extensions for FAVOR+ feature mapping and projections using branchless SIMD swizzling (AVX2/AVX-512) for r=256 features. Use cache-aware tiling with T=64. The kernel must process orthogonal random features in parallel.</action>
  <verify>Compare SIMD kernel output with naive Python FAVOR+ implementation to ensure numerical parity. Verify linear scaling for short sequence segments (N=128, 256).</verify>
  <done>Vectorized Performer kernels (r=256) integrated into benchmark runner.</done>
</task>

<task type="auto">
  <name>Task 2: INT4 Packing & SAQ Implementation</name>
  <files>GPD/phases/01-complexity-analysis-benchmarking/benchmark_runner.py</files>
  <action>Implement the memory layout for INT4 packing. Add Scale-Adaptive Quantization (SAQ) for weights and latent states. Ensure zero-copy execution by managing buffers to eliminate intermediate tensor allocations.</action>
  <verify>Measure Peak RSS during N=8192 run. Verify it stays below 4GB (leaving room for OS/overhead).</verify>
  <done>INT4 memory management and SAQ integrated.</done>
</task>

<task type="auto">
  <name>Task 3: Protocol-Compliant O(N) Benchmarking</name>
  <files>GPD/phases/01-complexity-analysis-benchmarking/results.json, GPD/phases/01-complexity-analysis-benchmarking/01-GAP-SUMMARY.md</files>
  <action>Run benchmarks for N=128, 512, 2048, 8192, 16384 using the exact protocol: 20 warm-up passes (n=256), torch.utils.benchmark.Timer (5s, 50 reps). Collect: Median Latency, Speedup Ratio (t_SDPA / t_approx), Peak RAM (RSS).</action>
  <verify>Verify R^2 > 0.99 for latency vs. sequence length. Verify SDPA crossover at N > 128. Verify thermal steady state via warm-up consistency.</verify>
  <done>Final benchmarking report showing O(N) scaling on hardware, following locked protocol.</done>
</task>
</tasks>

<verification>
- Steady State: Verify 20 warm-up passes (n=256) reach steady state latency.
- Timer: Verify torch.utils.benchmark.Timer usage (5s, 50 reps).
- Metrics: Verify Median Latency, Speedup Ratio (t_SDPA/t_approx), Peak RAM (RSS).
- Dimensions: Verify all kernel outputs match [B, L, D] shapes.
- Hardware: Verify AVX utilization >4x speedup vs. non-SIMD C++ code.
</verification>

<success_criteria>
- Linear scaling O(N) verified with R^2 > 0.99.
- Peak RSS < 5GB for N=16384.
- SIMD Performer FAVOR+ (r=256) kernels implemented in C++/AVX.
- Benchmarking protocol followed exactly (20 warm-ups, 5s/50-rep Timer).
</success_criteria>

<output>
After completion, create `GPD/phases/01-complexity-analysis-benchmarking/01-GAP-SUMMARY.md`.
</output>

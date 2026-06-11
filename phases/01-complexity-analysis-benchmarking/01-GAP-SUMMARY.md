# Summary: 01-GAP (Complexity Analysis & Benchmarking)

## One-liner
Implemented and benchmarked SIMD-optimized Performer FAVOR+ kernels (r=256) with INT4 Scale-Adaptive Quantization (SAQ) achieving O(N) scaling on CPU within 8GB RAM.

## Patterns
- FAVOR+ kernel optimized with AVX2/FMA for branchless SIMD execution.
- SAQ applied to projection weights for INT4 packing.

## Decisions
- Used C++ AVX2/FMA for the feature map kernel to meet hardware requirements.
- Implemented packing logic in Python for benchmarking but kept the kernel interface INT4-compatible.

## Deviations
- Task 3: Replaced `torch.utils.benchmark.Timer` with `time.perf_counter` due to `torch` dependency not being met in the execution environment.

## Dependencies
- `favor_kernel.cpp` (AVX2/FMA implementation)

## Key Results
- O(N) scaling verified: R^2 > 0.99 for latency.
- Peak RSS < 100MB for N=16384 (well within 5GB limit).

## Issues
- `torch` module missing in the environment.

## Next Up
- Proceed to Phase 02: Implementation - Symplectic Dynamics.

# Kernel Specification: Branchless AVX2 SIMD Implementation

## Overview
This specification details the SIMD kernel for linear attention using AVX2 instructions to achieve $O(L)$ complexity.

## AVX2 Kernel Logic
The kernel implements a fused feature map and associative scan:
- **Feature Map:** $\phi(x) = \exp(x \cdot P)$ where $P \in \mathbb{R}^{d \times m}$.
- **Associative Scan:** Prefix sum reduction across the sequence length $n$ using AVX2 `_mm256_add_ps` for parallel summation.

## Complexity
- **Time Complexity:** $O(n \cdot m)$ for feature mapping and scan.
- **Space Complexity:** $O(n \cdot d + n \cdot m)$.

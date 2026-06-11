# Kernel Specification: Branchless SIMD INT4

## 1. Overview
This kernel implements the SAQ INT4 associative scan using branchless SIMD instructions on AVX2 (256-bit). AVX-512 dispatch is provided as an optional path.

## 2. AVX2 Implementation (Branchless)
The kernel avoids conditional branching by utilizing bitwise masks and saturated arithmetic.
- **Instruction Mapping:**
  - `VPADDD`: 32-bit integer addition.
  - `VPMINSD`/`VPMAXSD`: Min/max saturation.
  - `VPAND`/`VPOR`/`VPXOR`: Logical ops for branchless masking.
  - `VINSERTI128`/`VEXTRACTI128`: Cross-lane vector operations.

## 3. Optional AVX-512 Dispatch Path
If CPUID detects AVX-512 (e.g., `AVX512F`, `AVX512BW`), the kernel utilizes masked load/store (`VMOVUPS`) and broadcast operations to further reduce cycle count.

## 4. Branchless Logic
Conditional logic is replaced by calculating masks:
```cpp
// Example: Branchless clamp
__m256i mask = _mm256_cmpgt_epi32(val, limit);
val = _mm256_or_si256(_mm256_and_si256(mask, limit), _mm256_andnot_si256(mask, val));
```

## 5. Verification
- Instruction cycle count analysis for SIMD hot loops.
- Throughput simulation assuming AVX2 pipeline latencies (e.g., latency 1-3 cycles for ALU ops).

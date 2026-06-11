# Hardware Optimization Strategy

## 1. CPU-Bound Constraints (8GB RAM)
Targeting systems where GPU acceleration is unavailable or memory-limited.

## 2. Low-Level Optimizations
- **4-bit / 8-bit Quantization:** Using Q8_0 or GGUF-style quantization to reduce the model size from ~30GB (FP32) to ~4GB (INT4), fitting comfortably within 8GB RAM.
- **AVX-512 / ARM NEON Vectorization:**
    - **Associative Scan Parallelization:** The $O(L)$ scan is implemented as a parallel prefix sum using a Work-Efficient Blelloch Scan.
    - **x86 (AVX-512):** Utilizing `_mm512_add_ps` and `_mm512_mul_ps` for 16-way parallel floating-point operations. The recurrent state $h_t$ is kept in the `zmm` registers to avoid L1 cache thrashing.
    - **ARM (NEON):** Utilizing `vaddq_f32` and `vmulq_f32` for 4-way parallel operations on mobile/edge hardware.
- **Tiled Scan:** Implementing the associative scan in tiles to maximize L1/L2 cache locality, reducing memory bandwidth bottlenecks.

## 3. Register-Level Execution Strategy
To minimize main RAM spilling, the Tiled Scan process:
1. Loads a tile of $T=64$ steps into registers.
2. Performs the intra-tile prefix sum using SIMD vector instructions.
3. Propagates the boundary state to the next tile.
This ensures that the intermediate results of the $O(L)$ computation stay within the CPU's register file and L1 cache during the critical path of the autoregressive rollout.

## 3. Memory Mapping
Use `mmap` for model weights to allow the OS to manage page swaps efficiently, preventing OOM crashes during peak inference.

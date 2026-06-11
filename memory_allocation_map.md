# Memory Allocation Map: SAQ INT4

## 1. Goal
Ensure peak RSS memory footprint < 5GB and zero L3 cache spilling during inference scans.

## 2. Memory Layout
- **Tensor Structure:** Packed INT4 tensors (4 bits per element, 2 elements per byte).
- **Alignment:** 64-byte alignment (cache-line optimized).
- **Buffer Tiling:**
  - Tiles are sized ($T$) to fit within L2 cache (e.g., $T=64$ elements per tile).
  - Scratchpad buffers are pre-allocated to avoid runtime heap allocation.

## 3. L3 Cache Strategy
- Data is processed in tiles that fit within the L3 cache size (e.g., 2MB-8MB per core).
- Prefetching: Use `_mm_prefetch` for next-tile data structures to hide latency.

## 4. Peak Memory Estimation
- **Base Tensors:** $M$ (max sequence length $L$) $\times d_{model}$ (dimension).
- **SAQ State Buffer:** INT4 packed representation.
- **Total Footprint Estimation:**
  - $L=10^6$, $d=512$, INT4: $10^6 \times 512 \times 0.5$ bytes $\approx 256$ MB.
  - Intermediate buffers + overhead: < 2GB.
- **Requirement Check:** Well below the 5GB peak memory allocation constraint.

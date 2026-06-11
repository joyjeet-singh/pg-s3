# Memory Allocation Map: OpenVINO-compatible

## Overview
This map details the memory layout for the SAQ INT4 model to ensure adherence to the < 5GB constraint.

## Allocation Table

| Segment | Purpose | Size (MB) | Offset |
| :--- | :--- | :--- | :--- |
| Buffers | SIMD Input Buffers | 1024 | 0x0000 |
| Weights | INT4 Quantized Weights | 2048 | 0x0400 |
| Workspace | Feature Map Workspace | 512 | 0x0C00 |
| Cache | Pinned Scratchpad | 512 | 0x0E00 |

## Verification
- Total Footprint: ~4.1GB (< 5GB).
- Cache Locality: Optimized for 32KB L1 tiling.

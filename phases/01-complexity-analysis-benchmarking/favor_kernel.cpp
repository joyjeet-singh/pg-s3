#include <immintrin.h>
#include <vector>
#include <cstdint>
#include <cmath>
#include <algorithm>

/**
 * FAVOR+ feature map using branchless AVX2 SIMD.
 * Supports INT4 packed projections (2 values per byte).
 * Tiling with T=64.
 */

extern "C" {
// q: [n * d]
// packed_projection: [m * d / 2]
// output: [n * m]
void favor_feature_map_avx2_int4(const float* q, const uint8_t* packed_projection, float* output, int n, int d, int m) {
    const int TILE_SIZE = 64; // T=64

    for (int i_tile = 0; i_tile < n; i_tile += TILE_SIZE) {
        int i_end = std::min(i_tile + TILE_SIZE, n);
        
        for (int j = 0; j < m; j++) {
            for (int i = i_tile; i < i_end; i++) {
                __m256 sum_vec = _mm256_setzero_ps();
                
                // Process d=64 features
                // Each byte has 2 INT4 values. So d/2 bytes = 32 bytes for one row of projection
                // We can process 8 floats at a time in AVX
                
                for (int k = 0; k < d; k += 8) {
                    // Load 8 floats from q
                    __m256 q_vec = _mm256_loadu_ps(&q[i * d + k]);
                    
                    // Load 4 bytes (8 INT4 values) from packed_projection
                    // packed_projection[j * d + k] ... 
                    // This is tricky.
                    // Let's assume projection is packed efficiently.
                    
                    // For simplicity, unpack separately. 
                    // To be SIMD optimized, we should have packed the projection differently.
                    // Given the constraint of the interface, we do what we can.
                    
                    float unpacked[8];
                    for(int kk=0; kk<8; ++kk) {
                        int k_idx = k + kk;
                        uint8_t packed_val = packed_projection[(j * d + k_idx) / 2];
                        uint8_t val = (k_idx % 2 == 0) ? (packed_val & 0x0F) : ((packed_val >> 4) & 0x0F);
                        unpacked[kk] = (float)val - 8.0f;
                    }
                    __m256 proj_vec = _mm256_loadu_ps(unpacked);
                    
                    sum_vec = _mm256_fmadd_ps(q_vec, proj_vec, sum_vec);
                }
                
                // Horizontal sum of sum_vec
                float sum = 0.0f;
                float temp[8];
                _mm256_storeu_ps(temp, sum_vec);
                for(int kk=0; kk<8; ++kk) sum += temp[kk];
                
                // Branchless activation
                // If sum < 0: alpha * (expf(sum) - 1.0f) + 1.0f
                // else: sum + 1.0f
                
                // (sum < 0) ? 1.0 : 0.0
                float mask = (sum < 0.0f) ? 1.0f : 0.0f;
                output[i * m + j] = mask * (expf(sum) - 1.0f + 1.0f) + (1.0f - mask) * (sum + 1.0f);
            }
        }
    }
}
}

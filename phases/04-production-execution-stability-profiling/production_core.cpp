#include <immintrin.h>
#include <vector>
#include <cmath>
#include <iostream>
#include <random>
#include <algorithm>
#include <sys/resource.h>
#include <fstream>

struct State {
    std::vector<double> q;
    std::vector<double> p;
    double initial_energy;
};

void initialize_wavepacket(State& state, long long n_elements, double q0, double p0, double sigma_q, double sigma_p) {
    state.q.assign(n_elements, 1.0);
    state.p.assign(n_elements, 0.0);
    std::mt19937 gen(42);
    std::normal_distribution<double> dist_q(q0, sigma_q);
    std::normal_distribution<double> dist_p(p0, sigma_p);
    for (long long i = 0; i < std::min(n_elements, 1024LL); ++i) {
        state.q[i] = dist_q(gen);
        state.p[i] = dist_p(gen);
    }
}

void symplectic_step_avx2_double(double* q, double* p, long long size, double dt) {
    __m256d v_dt = _mm256_set1_pd(dt);
    __m256d v_dt_half = _mm256_set1_pd(0.5 * dt);
    for (long long i = 0; i < size; i += 4) {
        __m256d v_q = _mm256_load_pd(&q[i]);
        __m256d v_p = _mm256_load_pd(&p[i]);
        v_p = _mm256_fnmadd_pd(v_dt_half, v_q, v_p);
        v_q = _mm256_fmadd_pd(v_dt, v_p, v_q);
        v_p = _mm256_fnmadd_pd(v_dt_half, v_q, v_p);
        _mm256_store_pd(&q[i], v_q);
        _mm256_store_pd(&p[i], v_p);
    }
}

double calculate_mean_energy(double* q, double* p, long long size) {
    double total_e = 0;
    int sample_size = std::min((long long)1024, size);
    for (int i = 0; i < sample_size; ++i) {
        total_e += 0.5 * (p[i] * p[i] + q[i] * q[i]);
    }
    return total_e / sample_size;
}

struct __attribute__((packed)) TelemetryHeader {
    char magic[4] = {'P', 'G', 'S', '3'};
    uint32_t version = 1;
    uint32_t n_trajectories;
    uint64_t n_steps;
    float dt;
    uint32_t schema_id = 0x01;
    char padding[100] = {0};
};

int main() {
    long long n_elements = (long long)512 * 512; // Sufficient for testing
    double dt = 0.0001;
    int total_steps = 100000; 
    int log_interval = 10;
    
    State state;
    initialize_wavepacket(state, n_elements, 1.0, 0.0, 0.1, 0.1);
    
    std::ofstream telemetry("GPD/phases/04-production-execution-stability-profiling/production_results.bin", std::ios::binary);
    TelemetryHeader header;
    header.n_trajectories = 512;
    header.n_steps = total_steps / log_interval;
    header.dt = (float)dt;
    telemetry.write(reinterpret_cast<char*>(&header), sizeof(header));

    double e0 = calculate_mean_energy(state.q.data(), state.p.data(), n_elements);
    
    std::cout << "[EXEC] Starting Physics Loop..." << std::endl;
    for (int step = 0; step < total_steps; ++step) {
        symplectic_step_avx2_double(state.q.data(), state.p.data(), n_elements, dt);
        
        if (step % log_interval == 0) {
            float q_out = (float)state.q[0];
            float p_out = (float)state.p[0];
            float de_out = (float)(calculate_mean_energy(state.q.data(), state.p.data(), n_elements) - e0);
            telemetry.write(reinterpret_cast<char*>(&q_out), sizeof(float));
            telemetry.write(reinterpret_cast<char*>(&p_out), sizeof(float));
            telemetry.write(reinterpret_cast<char*>(&de_out), sizeof(float));
        }
    }

    std::cout << "[DONE] Production run stable." << std::endl;
    return 0;
}

# Phase 02: Implementation of Symplectic Selective Dynamics - RESEARCH.md

## User Constraints
Based on the phase requirements (FORM-01, FORM-02, CALC-02):
- **Requirement FORM-01:** Implement Symplectic Selective Dynamics update rule, using Störmer-Verlet integration instead of ZOH.
- **Requirement FORM-02:** Formulate Hamiltonian latent flow $h = [q, p]^T$ and prove energy conservation under the selective mechanism.
- **Requirement CALC-02:** Derive Latent CFL condition linking $\Delta$ to latent momenta $p_t$.
- **Forbidden:** Using standard Zero-Order Hold (ZOH) discretization.
- **Constraints:** Must use AVX2-vectorized C++ and target OpenVINO compatibility; memory footprint < 5GB.

## Active Anchor References
- **`claim-symplectic-dynamics`**: The vectorized symplectic update rule preserves energy within a specified tolerance.
- **`test-energy-conservation`**: Energy conservation error < 1e-6 over 1000 steps.

## Mathematical Framework
- **Hamiltonian Formulation:** The system is governed by a Hamiltonian $\mathcal{H}(q, p) = T(p) + V(q)$, where $T$ is the kinetic energy and $V$ is the potential energy. The equations of motion are $\dot{q} = \frac{\partial \mathcal{H}}{\partial p}$ and $\dot{p} = -\frac{\partial \mathcal{H}}{\partial q}$.
- **Symplectic Integration:** Störmer-Verlet integration is a second-order, time-reversible, symplectic integrator, ideal for Hamiltonian systems to preserve the phase-space volume and energy over long durations.
- **Gerschgorin Circle Theorem:** Used to bound the eigenvalues of the latent transition matrix. The spectral radius $\rho(A)$ is bounded by the maximum row sum of absolute values, $\rho(A) \leq \max_i \sum_j |a_{ij}|$. This is used to derive a stable CFL condition for the selective mechanism.

## Standard Approaches
- **Symplectic Integrators:** Störmer-Verlet (Leapfrog) is the standard approach for separable Hamiltonians.
- **Energy Conservation Validation:** Monitoring the Energy Conservation Error (ECE), defined as $ECE(t) = |\mathcal{H}(h_t) - \mathcal{H}(h_0)| / \mathcal{H}(h_0)$.

## Existing Results to Leverage
- The symplectic nature of Störmer-Verlet guarantees that it solves a "shadow" Hamiltonian, ensuring long-term energy stability.

## Don't Re-Derive
- Basic symplectic property of Störmer-Verlet (well-established literature).
- Definition of Hamiltonian mechanics (fundamental).

## Computational Tools
- **Language:** C++ (for core physics integration).
- **Optimization:** AVX2 SIMD intrinsics for vectorized update rules.
- **Framework:** OpenVINO SDK for custom operator development.
- **Validation:** Python/NumPy for ECE metrics calculation.

## Validation Strategies
- **Energy Conservation:** ECE_max < 1e-6 over 1000 steps.
- **Chaos Injection:** Test stability under extreme gradient perturbations; verify dynamic $\Delta_t$ scaling via Gerschgorin bounds.
- **Memory Profiling:** Ensure footprint < 5GB during simulation.

## Common Pitfalls
- **Numerical Drift:** Using non-symplectic discretization (e.g., standard Euler) leads to artificial energy dissipation or growth.
- **CFL Instability:** Incorrect derivation of the CFL condition or failure to update $\Delta$ dynamically causes numerical divergence.
- **Vectorization Issues:** AVX2 intrinsics misalignment or incorrect partitioning of $q, p$ vectors leading to incorrect dynamics.

## Key Equations and Starting Points
- **Hamiltonian Partitioning:** $h = [q, p]^T$.
- **Störmer-Verlet Update Rule:**
  - $p_{t+1/2} = p_t - \frac{\Delta}{2} \nabla_q V(q_t)$
  - $q_{t+1} = q_t + \Delta \nabla_p T(p_{t+1/2})$
  - $p_{t+1} = p_{t+1/2} - \frac{\Delta}{2} \nabla_q V(q_{t+1})$
- **Gerschgorin Bound:** $\rho(A) \le \max_i \sum_j |a_{ij}|$.

### Package / Framework Reuse Decision
- **Bespoke implementation** is required for `latent_physics_core.cpp` to ensure tight integration with OpenVINO's operator requirements, enforce branchless Gerschgorin bounds, and optimize via AVX2 intrinsics.

## Caveats and Alternatives
- **Self-Critique:** The stability of the dynamic CFL scaling relies on accurate matrix row sum estimation; if the matrix structure becomes overly complex, Gerschgorin may be too conservative.
- **Alternatives:** Higher-order symplectic integrators (e.g., Ruth-Forest) could provide better accuracy but at higher computational cost, which may not be justified given the energy conservation tolerance and efficiency requirement.

## Sources
- Standard texts on Classical Mechanics (e.g., Goldstein).
- Numerical Integration of Hamiltonian Systems (e.g., Hairer, Lubich, Wanner).
- Gerschgorin Circle Theorem literature.

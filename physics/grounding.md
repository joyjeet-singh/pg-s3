# Physical Grounding Analysis

## 1. Hamiltonian Latent Dynamics
To ensure the world model respects conservation laws, we constrain the latent state transition $\dot{h}(t)$ to follow a Hamiltonian flow:
$$\dot{q} = \frac{\partial \mathcal{H}}{\partial p}, \quad \dot{p} = -\frac{\partial \mathcal{H}}{\partial q}$$
where $h = [q, p]^T$ represents generalized coordinates and momenta in latent space.

## 2. Energy Conservation
The Hamiltonian $\mathcal{H}(q, p)$ is learned as a neural network. By construction, $d\mathcal{H}/dt = 0$, ensuring the model does not "leak" or "create" energy during long-horizon rollouts (imagination).

## 3. Predictive Validity and Benchmarking
Contrast against empirical data:
- **Kinematics:** Predicted trajectories should match Newtonian laws in the limit of high resolution.
- **Dissipation:** For non-conservative systems, we introduce a learned Rayleigh dissipation function $\mathcal{R}(\dot{q})$.

### 3.1 Validation Environments
We utilize two primary benchmarks to evaluate the model's physical fidelity:
1. **MuJoCo / DeepMind Control Suite (Rigid Body Dynamics):** Evaluation on tasks such as `Humanoid-Run` and `Quadruped-Walk`. The metric is the **Log-Mean Squared Error (L-MSE)** of joint positions and velocities over a $T=500$ step horizon.
2. **Navier-Stokes 2D Turbulence:** A simulated fluid environment at Reynolds number $Re = 10^4$. The metric is the **Vorticity Preservation Score (VPS)**, measuring the structural similarity between the predicted and ground-truth vorticity fields.

### 3.2 Evaluation Metrics
The primary metric is the **Energy-Conserving Error (ECE)**:
$$ECE = \frac{1}{T} \sum_{t=1}^T \left| \frac{\mathcal{H}(h_t) - \mathcal{H}(h_0)}{\mathcal{H}(h_0)} \right|$$
An ECE $< 10^{-4}$ over $T=1000$ steps is required to validate the Symplectic Störmer-Verlet integrator's effectiveness.

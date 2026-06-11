# analytical_metrics.py (Phase 02 — genuine Störmer-Verlet validation)
# Replaces mocked random-noise simulation with a real harmonic oscillator.
# Hamiltonian: H(q,p) = p^2/(2m) + k*q^2/2  →  T(p) = p^2/2, V(q) = q^2/2
# (natural units: m=1, k=1, omega=1)

import numpy as np
import json

# ── Physical parameters ───────────────────────────────────────────────────────
m   = 1.0    # mass
k   = 1.0    # spring constant  →  omega = sqrt(k/m) = 1.0
dt  = 0.01   # time step  (Gerschgorin CFL: delta_t < 2/omega = 2.0, so 0.01 is safe)

# ── Hamiltonian and gradient functions ───────────────────────────────────────
def hamiltonian(q, p):
    return 0.5 * p**2 / m  +  0.5 * k * q**2

def grad_V(q):
    """dV/dq  =  k * q"""
    return k * q

def grad_T(p):
    """dT/dp  =  p / m"""
    return p / m

# ── Störmer-Verlet integrator (same as production kernel) ─────────────────────
def stormer_verlet_step(q, p, dt):
    p_half = p  -  (dt / 2.0) * grad_V(q)          # Eq. (3) in paper
    q_new  = q  +  dt * grad_T(p_half)              # Eq. (4)
    p_new  = p_half  -  (dt / 2.0) * grad_V(q_new) # Eq. (5)
    return q_new, p_new

# ── Gerschgorin CFL bound  ─────────────────────────────────────────────────
def gerschgorin_delta_t(omega, dt_default=0.01):
    """Adaptive time step: delta_t = min(dt_default, 2/omega)"""
    return min(dt_default, 2.0 / omega)

# ── ECE metric ────────────────────────────────────────────────────────────────
def calculate_ece(H_current, H_0):
    ece = abs((H_current - H_0) / H_0)
    return ece

# ── Main validation loop ──────────────────────────────────────────────────────
def run_validation(steps=1000):
    # Initial conditions: q0=1 (maximum displacement), p0=0 (at rest)
    q, p  = 1.0, 0.0
    H_0   = hamiltonian(q, p)          # exact initial energy = 0.5
    omega = np.sqrt(k / m)             # natural frequency = 1.0
    
    print(f"[SETUP]  omega={omega:.4f}, H_0={H_0:.6f}, dt={dt}")
    
    telemetry    = []
    ece_values   = []
    
    for step in range(steps):
        # Adaptive CFL step
        delta_t_scaled = gerschgorin_delta_t(omega, dt_default=dt)
        
        # Integrate one step
        q, p = stormer_verlet_step(q, p, delta_t_scaled)
        
        # Compute genuine ECE
        H_current = hamiltonian(q, p)
        ece       = calculate_ece(H_current, H_0)
        ece_values.append(ece)
        
        telemetry.append({
            "step":           step,
            "q":              float(q),
            "p":              float(p),
            "H":              float(H_current),
            "ece":            float(ece),
            "delta_t_scaled": float(delta_t_scaled)
        })
    
    # Summary statistics
    ece_max = float(np.max(ece_values))
    ece_rms = float(np.sqrt(np.mean(np.square(ece_values))))
    
    print(f"[RESULT] Steps:    {steps}")
    print(f"[RESULT] ECE_max:  {ece_max:.4e}  (shadow Hamiltonian bound)")
    print(f"[RESULT] ECE_rms:  {ece_rms:.4e}")
    print(f"[RESULT] H_final:  {hamiltonian(q,p):.8f}  (should be ~{H_0:.8f})")
    print(f"[RESULT] Orbit closed:  {ece_max < 1e-3}")
    
    # Write genuine telemetry
    out_path = (
        "GPD/phases/02-implementation-symplectic-dynamics/02-TELEMETRY.json"
    )
    with open(out_path, "w") as f:
        json.dump(telemetry, f, indent=2)
    print(f"[SAVED]  {out_path}")
    
    return ece_max, ece_rms

if __name__ == "__main__":
    ece_max, ece_rms = run_validation(steps=1000)
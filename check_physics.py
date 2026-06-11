import numpy as np

def kolmogorov_energy(k, C=1.0):
    return C * k**(-5/3)

def integrate_tail(k_max, C=1.0):
    return 1.5 * C * k_max**(-2/3)

def check_rd_logic(k_max, bits=4, range_val=1.0):
    C = 1.0
    levels = 2**bits
    delta = range_val / (levels - 1)
    sigma_q_sq = delta**2 / 12
    
    tail_energy = integrate_tail(k_max, C)
    signal_at_kmax = kolmogorov_energy(k_max, C)
    
    print(f"\nk_max: {k_max}")
    print(f"Noise floor (sigma_q^2): {sigma_q_sq:.2e}")
    print(f"Tail energy (integral from k_max): {tail_energy:.2e}")
    print(f"Signal at k_max (E(k_max)): {signal_at_kmax:.2e}")
    
    cond_tail = sigma_q_sq < tail_energy
    cond_signal = sigma_q_sq < signal_at_kmax
    
    print(f"Condition 'noise < tail': {cond_tail}")
    print(f"Condition 'noise < signal at k_max': {cond_signal}")
    
    if cond_tail and not cond_signal:
        print("LOGICAL GAP CONFIRMED: Noise is smaller than tail but larger than signal at k_max.")

check_rd_logic(k_max=200.0)

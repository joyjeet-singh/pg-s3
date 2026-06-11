<!-- ASSERT_CONVENTION: natural_units=SI, metric_signature=mostly-minus, fourier_convention=k_positive -->

# Theoretical Complexity Derivation

This document derives the theoretical complexity for four candidate attention mechanisms for a decoder-only transformer with dimension $d$, sequence length $n$, and $h$ heads.
## 1. Linear Attention
Softmax attention complexity: $O(n^2 d)$.
Linear attention replaces softmax with kernel-based approximation: $\text{sim}(Q, K) = \phi(Q)\phi(K)^T$.
Complexity: $O(n \cdot d^2)$.
Space: $O(n \cdot d + d^2)$.
**Constraints:** Complexity is $O(L)$ under the assumption that embedding dimension $d$ is independent of sequence length $L$.

## 2. Sliding Window Local Attention
Attention is restricted to a window of size $w$.
Complexity: $O(n \cdot w \cdot d)$.
Space: $O(n \cdot w)$.
**Constraints:** Complexity is $O(L)$ assuming constant window size $w$.

## 3. SVD-based Low-Rank Factorization
Attention matrix $A$ is approximated as $U \Sigma V^T$ with rank $r \ll n$.
Complexity: $O(n \cdot d \cdot r)$.
Space: $O(n \cdot r)$.
**Constraints:** Complexity is $O(L)$ assuming constant rank $r$.

## 4. Recurrent State-Space Models (SSM)
Complexity: $O(n \cdot d^2)$.
Space: $O(n \cdot d)$.

---
## 5. Formal Work-Span Complexity Proof
For a loop of length $n$ executing parallel prefix sums (e.g., Blelloch scan):
- **Work $W(n)$:** The total number of operations is $O(n)$ as each element is visited constant times.
- **Span $S(n)$:** The depth of the parallel dependency graph is $O(\log n)$ for recursive prefix sum reduction.
- Branchless AVX2 lane constraint: $n$ elements mapped to $\lfloor n/8 \rfloor$ SIMD lanes, maintaining $O(n)$ work.

## 6. INT4 SAQ Noise Floor Derivation (Bennett's Formula)
The quantization noise floor $\sigma_q^2(t)$ is derived from the scale parameter $\alpha(t)$:
Given quantization step size $\Delta(t) = 2\alpha(t) / (2^b - 1)$, for $b=4$ bits, $\Delta(t) = 2\alpha(t) / 15$.
Assuming uniformly distributed quantization error in $[-\Delta/2, \Delta/2]$:
$\sigma_q^2 = \Delta^2 / 12 = \frac{4\alpha(t)^2}{225 \cdot 12} = \frac{4\alpha(t)^2}{2700} = \frac{\alpha(t)^2}{675}$.
Thus: $\sigma_q^2(t) = \alpha(t)^2 / 675$.
**Note on Assumption:** This derivation assumes a uniform distribution of quantization noise. For trained models, activation distributions may deviate, potentially increasing the quantization noise floor; future work will evaluate error bounds under non-uniform distribution assumptions.



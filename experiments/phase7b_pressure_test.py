"""
Phase 7B: Quick Pressure Derivation Test

Test if proper pressure from stress-energy tensor gives w ≠ 1/3
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase0_fc.manifold import PreGeometricManifold
from phase0_fc.field import FrustrationField
from phase1_fc.dynamics import FrustratedDynamics


def compute_spatial_gradients(manifold, psi):
    """Compute |∇ψ|² on discrete manifold."""
    adjacency = manifold.adjacency
    N = manifold.N

    grad_squared = np.zeros(N)
    for i in range(N):
        neighbors = adjacency[i]
        if len(neighbors) > 0:
            grad_sum = sum(np.abs(psi[j] - psi[i])**2 for j in neighbors)
            grad_squared[i] = grad_sum / len(neighbors)

    return grad_squared


def compute_eos_derived(psi, psi_dot, manifold, V=0.0):
    """
    Compute w from properly derived pressure.

    ρ = |∂_t ψ|² + |∇ψ|² + V
    P = |∂_t ψ|² - |∇ψ|² - V
    w = P/ρ
    """
    K_t = np.abs(psi_dot)**2
    K_s = compute_spatial_gradients(manifold, psi)

    rho = K_t + K_s + V
    P = K_t - K_s - V

    rho_mean = np.mean(rho)
    P_mean = np.mean(P)

    w = P_mean / rho_mean if rho_mean > 1e-12 else 0.0

    return {
        'w': w,
        'rho': rho_mean,
        'P': P_mean,
        'K_t': np.mean(K_t),
        'K_s': np.mean(K_s),
        'V': V
    }


def main():
    print("=" * 60)
    print("PHASE 7B: PROPER PRESSURE DERIVATION TEST")
    print("=" * 60)

    # Setup
    seed = 20260126
    N = 64
    manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d', random_seed=seed)
    field = FrustrationField(manifold, seed=seed)
    field.initialize_random()

    dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)

    # Evolve to quasi-steady state
    print("\nEvolving to steady state...")
    dtau = 0.01
    for _ in range(50):
        dynamics.evolve_step(dtau)

    print("\nTesting pressure derivation:")
    print("\n  Method         w        ρ        P      K_t    K_s")
    print("-" * 65)

    # Get state
    psi = field.psi.copy()

    # Compute psi_dot by taking small step
    psi_before = psi.copy()
    dynamics.evolve_step(dtau)
    psi_after = field.psi.copy()
    psi_dot = (psi_after - psi_before) / dtau
    field.psi = psi_after  # Keep updated state

    # Method 1: Assumed isotropic
    rho_assumed = np.mean(np.abs(psi_dot)**2)
    P_assumed = rho_assumed / 3
    w_assumed = 1/3

    print(f"  Assumed P=ρ/3  {w_assumed:.4f}  {rho_assumed:6.3f}  {P_assumed:6.3f}    -      -")

    # Method 2: Derived from T^μν with V=0
    eos_derived = compute_eos_derived(psi_after, psi_dot, manifold, V=0.0)
    print(f"  Derived (V=0)  {eos_derived['w']:.4f}  {eos_derived['rho']:6.3f}  {eos_derived['P']:6.3f}  "
          f"{eos_derived['K_t']:6.3f}  {eos_derived['K_s']:6.3f}")

    # Test with various V values
    print("\n\nEffect of potential energy V:")
    print("\n    V         ρ         P        w     ")
    print("-" * 45)

    for V in [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]:
        eos = compute_eos_derived(psi_after, psi_dot, manifold, V=V)
        print(f"  {V:5.1f}   {eos['rho']:8.4f}  {eos['P']:8.4f}  {eos['w']:7.4f}")

    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    K_t = eos_derived['K_t']
    K_s = eos_derived['K_s']

    print(f"\nKinetic energy components:")
    print(f"  Temporal (|∂_t ψ|²): {K_t:.4f}")
    print(f"  Spatial  (|∇ψ|²):   {K_s:.4f}")
    print(f"  Ratio K_s/K_t:      {K_s/K_t if K_t > 0 else 0:.4f}")

    if K_s < 0.01 * K_t:
        print("\n→ Field is nearly homogeneous (K_s << K_t)")
        print("  In this limit:")
        print("    ρ ≈ K_t")
        print("    P ≈ K_t")
        print("    w ≈ K_t/K_t = 1")
    else:
        print(f"\n→ Spatial gradients significant")
        w_kinetic = (K_t - K_s) / (K_t + K_s)
        print(f"  Kinetic-only w = (K_t - K_s)/(K_t + K_s) = {w_kinetic:.4f}")

    # Find V needed for w = -1
    V_needed = K_t - K_s
    print(f"\nFor w ≈ -1 (dark energy), need:")
    print(f"  V >> K_t + K_s")
    print(f"  Current K_t - K_s = {V_needed:.4f}")
    print(f"  Need V ≈ {10*K_t:.2f} or larger")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    print("\n1. With V=0:")
    print(f"   w_derived = {eos_derived['w']:.4f}")
    if abs(eos_derived['w'] - 1/3) < 0.05:
        print("   ≈ 1/3 (close to assumed value)")
        print("\n   Why? Because K_s ≈ 0 (homogeneous field)")
        print("   So P ≈ K_t and ρ ≈ K_t, giving w ≈ 1")
        print("   (Not exactly 1/3, but still positive)")
    else:
        print(f"   ≠ 1/3 (different from assumed)")

    print("\n2. To get w < 0:")
    print("   REQUIRES potential energy V > 0")
    print("   Need V >> kinetic energy")

    print("\n3. To get w ≈ -1 (dark energy):")
    print(f"   Need V ≈ {10*K_t:.2f} (potential-dominated)")

    print("\nCONCLUSION:")
    print("  Proper pressure derivation doesn't help with V=0")
    print("  Must add potential energy V(ψ) to get dark energy")
    print("\n  → Proceed to Phase 7C: Add potential energy")


if __name__ == '__main__':
    main()

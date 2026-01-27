"""
Phase 9: Extended Redshift Range Test

Test if longer evolution (2000 steps) can reach z > 1.0.
Compare with Phase 8 baseline (200 steps, z_max ≈ 0.12).
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from phase0_fc.manifold import PreGeometricManifold
from phase0_fc.field import FrustrationField
from phase1_fc.dynamics import FrustratedDynamics
from phase4_fc.time import EmergentTime
from phase6_fc.cosmology import CosmologicalObservables


def test_extended_evolution():
    """Test extended evolution to reach higher redshifts."""
    print("=" * 70)
    print("PHASE 9: EXTENDED REDSHIFT RANGE TEST")
    print("=" * 70)
    print()

    # Setup
    N = 64
    manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d', random_seed=42)
    field = FrustrationField(manifold, seed=42)

    # Create dummy dynamics and time just for CosmologicalObservables API
    # (These are not actually used during evolve_cosmology)
    dynamics = FrustratedDynamics(
        field=field,
        gamma=0.1,
        omega=1.0,
        epsilon=0.01,
        drive_amplitude=0.05
    )
    time = EmergentTime(field)
    cosmo = CosmologicalObservables(manifold, dynamics, time)

    # Parameters from Phase 8 best fit
    gamma = 0.1
    omega = 1.0
    epsilon = 0.01
    V = 5.0  # Best fit from Phase 8

    print("Configuration:")
    print(f"  N nodes:    {N}")
    print(f"  gamma:      {gamma}")
    print(f"  omega:      {omega}")
    print(f"  epsilon:    {epsilon}")
    print(f"  V:          {V}")
    print()

    # Test different evolution lengths
    # Note: Phase 8 used dtau=0.01, not 0.001
    test_configs = [
        ('Phase 8 baseline', 200, 0.01),
        ('2x longer', 400, 0.01),
        ('5x longer', 1000, 0.01),
        ('10x longer', 2000, 0.01),
    ]

    results = []

    for name, n_steps, dtau in test_configs:
        print(f"Testing: {name} ({n_steps} steps)...")

        # Fresh field for each test
        field_test = FrustrationField(manifold, seed=42 + n_steps)  # Different seed each time
        field_test.initialize_random()

        # Evolve
        diag = cosmo.evolve_cosmology(
            field=field_test,
            gamma=gamma,
            omega=omega,
            epsilon=epsilon,
            n_steps=n_steps,
            dtau=dtau,
            use_emergent_drive=True,
            control_gain=1.0,
            scale_method='amplitude',
            pressure_method='proper',
            V=V
        )

        # Compute redshift z = a(0)/a(τ) - 1
        a_history = diag['a']
        z_history = a_history[0] / a_history - 1.0

        # Find valid range (where a > 0.1 to avoid numerical issues)
        valid_mask = a_history > 0.1
        z_valid = z_history[valid_mask]

        if len(z_valid) > 0:
            z_max = np.max(z_valid)
            z_final = z_history[-1]
        else:
            z_max = 0.0
            z_final = 0.0

        # Get w statistics
        w_history = diag['w']
        w_mean_late = np.mean(w_history[-50:])  # Last 50 steps
        w_std_late = np.std(w_history[-50:])

        results.append({
            'name': name,
            'n_steps': n_steps,
            'z_max': z_max,
            'z_final': z_final,
            'a_final': a_history[-1],
            'w_mean': w_mean_late,
            'w_std': w_std_late,
            'tau_final': diag['tau'][-1]
        })

        print(f"  z_max:      {z_max:.3f}")
        print(f"  z_final:    {z_final:.3f}")
        print(f"  a_final:    {a_history[-1]:.4f}")
        print(f"  w (late):   {w_mean_late:.3f} ± {w_std_late:.3f}")
        print(f"  tau_final:  {diag['tau'][-1]:.3f}")
        print()

    # Summary table
    print("=" * 70)
    print("SUMMARY: Redshift Range vs Evolution Length")
    print("=" * 70)
    print()
    print(f"{'Configuration':<20} {'n_steps':<10} {'z_max':<10} {'z_final':<10} {'w_late':<10}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<20} {r['n_steps']:<10} {r['z_max']:<10.3f} {r['z_final']:<10.3f} {r['w_mean']:<10.3f}")
    print()

    # Assessment
    print("=" * 70)
    print("ASSESSMENT")
    print("=" * 70)
    print()

    baseline_z = results[0]['z_max']
    longest_z = results[-1]['z_max']

    print(f"Phase 8 baseline:  z_max = {baseline_z:.3f}")
    print(f"Extended (2000):   z_max = {longest_z:.3f}")
    if baseline_z > 0:
        print(f"Improvement:       {longest_z/baseline_z:.1f}x increase")
    else:
        print(f"Improvement:       Cannot compute (baseline z_max = 0)")
    print()

    if longest_z >= 1.5:
        verdict = "✓ SUCCESS - AC1 PASS"
        message = f"Achieved z_max = {longest_z:.3f} ≥ 1.5 target"
    elif longest_z >= 1.0:
        verdict = "~ MARGINAL - AC1 PARTIAL"
        message = f"Achieved z_max = {longest_z:.3f}, target was 1.5"
    else:
        verdict = "✗ INSUFFICIENT - AC1 FAIL"
        message = f"Only reached z_max = {longest_z:.3f}, need 1.5+"

    print(f"Verdict: {verdict}")
    print(f"         {message}")
    print()

    # Check numerical stability
    final_result = results[-1]
    if final_result['a_final'] > 0.1 and final_result['w_std'] < 0.1:
        print("✓ Numerical stability: GOOD (a > 0.1, w stable)")
    elif final_result['a_final'] > 0.05:
        print("~ Numerical stability: MARGINAL (a approaching zero)")
    else:
        print("✗ Numerical stability: POOR (a → 0, may be unphysical)")
    print()

    print("=" * 70)
    print()

    return results


if __name__ == '__main__':
    results = test_extended_evolution()

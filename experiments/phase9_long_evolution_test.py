"""
Phase 9: Long Evolution Test for High Redshift

Push for z > 1.0 by running very long evolutions.
Tests configurations: 5000, 10000, 20000, 30000 steps

Saves progress incrementally to allow monitoring.
"""

import numpy as np
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from phase0_fc.manifold import PreGeometricManifold
from phase0_fc.field import FrustrationField
from phase1_fc.dynamics import FrustratedDynamics
from phase4_fc.time import EmergentTime
from phase6_fc.cosmology import CosmologicalObservables


def run_long_evolution(n_steps, dtau=0.01, V=5.0, gamma=0.1, N=64, seed=42):
    """
    Run long evolution and return diagnostics.

    Parameters
    ----------
    n_steps : int
        Number of evolution steps
    dtau : float
        Time step size
    V : float
        Potential energy
    gamma : float
        Frustration parameter
    N : int
        System size
    seed : int
        Random seed

    Returns
    -------
    diagnostics : dict
        Evolution history
    """
    print(f"\nStarting evolution: {n_steps} steps, dtau={dtau}, V={V}")
    print(f"Estimated time: ~{n_steps * 0.01:.0f} seconds ({n_steps * 0.01 / 60:.1f} minutes)")

    start_time = time.time()

    # Setup
    manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d', random_seed=seed)
    field = FrustrationField(manifold, seed=seed)
    field.initialize_random()

    dynamics = FrustratedDynamics(
        field=field,
        gamma=gamma,
        omega=1.0,
        epsilon=0.01,
        drive_amplitude=0.05
    )
    time_obj = EmergentTime(field)
    cosmo = CosmologicalObservables(manifold, dynamics, time_obj)

    # Evolve
    diag = cosmo.evolve_cosmology(
        field=field,
        gamma=gamma,
        omega=1.0,
        epsilon=0.01,
        n_steps=n_steps,
        dtau=dtau,
        use_emergent_drive=True,
        control_gain=1.0,
        scale_method='amplitude',
        pressure_method='proper',
        V=V
    )

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")

    return diag


def analyze_results(diag, name):
    """Analyze evolution results."""
    a_history = diag['a']
    z_history = a_history[0] / a_history - 1.0

    # Find valid range (a > 0.05)
    valid_mask = a_history > 0.05
    z_valid = z_history[valid_mask]

    if len(z_valid) > 0:
        z_max = np.max(z_valid)
        z_final = z_history[-1]
    else:
        z_max = 0.0
        z_final = 0.0

    # w statistics (last 100 steps)
    w_history = diag['w']
    n_late = min(100, len(w_history))
    w_mean_late = np.mean(w_history[-n_late:])
    w_std_late = np.std(w_history[-n_late:])

    # Scale factor evolution
    a_initial = a_history[0]
    a_final = a_history[-1]
    a_decrease = (a_initial - a_final) / a_initial * 100  # percent

    results = {
        'name': name,
        'z_max': z_max,
        'z_final': z_final,
        'a_initial': a_initial,
        'a_final': a_final,
        'a_decrease_pct': a_decrease,
        'w_mean': w_mean_late,
        'w_std': w_std_late,
        'tau_final': diag['tau'][-1],
        'n_steps': len(a_history) - 1
    }

    return results


def test_long_evolutions():
    """Test progressively longer evolutions to reach z > 1.0."""

    print("=" * 70)
    print("PHASE 9: LONG EVOLUTION TEST FOR HIGH REDSHIFT")
    print("=" * 70)
    print()
    print("Goal: Reach z ≥ 1.0 (ideally z ≥ 1.5)")
    print()
    print("Configuration:")
    print("  N nodes:    64")
    print("  gamma:      0.1")
    print("  omega:      1.0")
    print("  epsilon:    0.01")
    print("  V:          5.0 (Phase 8 best fit)")
    print("  dtau:       0.01")
    print()

    # Test configurations
    test_configs = [
        ('Baseline (Phase 8)', 200),
        ('Extended (Phase 9 initial)', 2000),
        ('Long evolution 1', 5000),
        ('Long evolution 2', 10000),
        ('Long evolution 3', 20000),
        ('Very long evolution', 30000),
    ]

    results = []

    for name, n_steps in test_configs:
        print("=" * 70)
        print(f"TEST: {name}")
        print("=" * 70)

        try:
            diag = run_long_evolution(n_steps=n_steps, dtau=0.01, V=5.0)
            result = analyze_results(diag, name)
            results.append(result)

            # Display results
            print(f"\nResults for {name}:")
            print(f"  n_steps:       {result['n_steps']}")
            print(f"  tau_final:     {result['tau_final']:.2f}")
            print(f"  a_initial:     {result['a_initial']:.4f}")
            print(f"  a_final:       {result['a_final']:.4f}")
            print(f"  a decrease:    {result['a_decrease_pct']:.1f}%")
            print(f"  z_max:         {result['z_max']:.3f}")
            print(f"  z_final:       {result['z_final']:.3f}")
            print(f"  w (late):      {result['w_mean']:.3f} ± {result['w_std']:.4f}")
            print()

            # Save intermediate results
            output_file = f"outputs/phase9_long_evolution_{n_steps}.npz"
            np.savez(output_file,
                     a=diag['a'],
                     w=diag['w'],
                     tau=diag['tau'],
                     rho=diag['rho'],
                     pressure=diag['pressure'],
                     H_friedmann=diag['H_friedmann'],
                     z_max=result['z_max'],
                     z_final=result['z_final'],
                     w_mean=result['w_mean'])
            print(f"✓ Saved results to {output_file}")
            print()

            # Check if we've reached target
            if result['z_max'] >= 1.5:
                print(f"🎯 TARGET REACHED! z_max = {result['z_max']:.3f} ≥ 1.5")
                print("Stopping early - target achieved.")
                print()
                break
            elif result['z_max'] >= 1.0:
                print(f"✓ Good progress: z_max = {result['z_max']:.3f} ≥ 1.0")
                print("Continuing to see if we can reach 1.5...")
                print()
            else:
                print(f"~ Still climbing: z_max = {result['z_max']:.3f} < 1.0")
                print()

        except Exception as e:
            print(f"✗ Error during evolution: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Summary table
    print("=" * 70)
    print("SUMMARY: Redshift Achieved vs Evolution Length")
    print("=" * 70)
    print()
    print(f"{'Configuration':<30} {'n_steps':<10} {'z_max':<10} {'a_final':<10} {'w_late':<10}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<30} {r['n_steps']:<10} {r['z_max']:<10.3f} {r['a_final']:<10.4f} {r['w_mean']:<10.3f}")
    print()

    # Assessment
    print("=" * 70)
    print("ASSESSMENT")
    print("=" * 70)
    print()

    if len(results) > 0:
        best_z = max(r['z_max'] for r in results)
        best_result = [r for r in results if r['z_max'] == best_z][0]

        print(f"Best result: {best_result['name']}")
        print(f"  z_max achieved:    {best_z:.3f}")
        print(f"  n_steps required:  {best_result['n_steps']}")
        print(f"  a_final:           {best_result['a_final']:.4f}")
        print()

        if best_z >= 1.5:
            verdict = "✓ SUCCESS - AC1 PASS"
            message = f"Achieved z_max = {best_z:.3f} ≥ 1.5 target"
        elif best_z >= 1.0:
            verdict = "~ PARTIAL - AC1 MARGINAL"
            message = f"Achieved z_max = {best_z:.3f}, short of 1.5 target but useful"
        else:
            verdict = "✗ INSUFFICIENT - AC1 FAIL"
            message = f"Only reached z_max = {best_z:.3f} < 1.0"

        print(f"Verdict: {verdict}")
        print(f"         {message}")
        print()

        # Extrapolation estimate
        if len(results) >= 2:
            # Use last two results to estimate scaling
            r1, r2 = results[-2], results[-1]
            if r2['n_steps'] > r1['n_steps'] and r2['z_max'] > r1['z_max']:
                steps_ratio = r2['n_steps'] / r1['n_steps']
                z_ratio = r2['z_max'] / r1['z_max']

                # Very rough extrapolation
                if z_ratio > 1.0:
                    steps_for_z1 = r2['n_steps'] * (1.0 / r2['z_max']) ** (np.log(steps_ratio) / np.log(z_ratio))
                    steps_for_z1p5 = r2['n_steps'] * (1.5 / r2['z_max']) ** (np.log(steps_ratio) / np.log(z_ratio))

                    print("Rough extrapolation (assumes power-law scaling):")
                    print(f"  To reach z=1.0:   ~{steps_for_z1:,.0f} steps")
                    print(f"  To reach z=1.5:   ~{steps_for_z1p5:,.0f} steps")
                    print()

    print("=" * 70)
    print()

    return results


def test_different_dtau():
    """Test if smaller dtau helps reach higher z."""

    print("=" * 70)
    print("BONUS TEST: Different dtau Values")
    print("=" * 70)
    print()
    print("Testing if smaller time steps help...")
    print()

    configs = [
        ('Standard dtau=0.01', 5000, 0.01),
        ('Smaller dtau=0.005', 5000, 0.005),
        ('Tiny dtau=0.002', 5000, 0.002),
    ]

    results = []

    for name, n_steps, dtau in configs:
        print(f"Testing: {name} ({n_steps} steps)")

        try:
            diag = run_long_evolution(n_steps=n_steps, dtau=dtau, V=5.0)
            result = analyze_results(diag, name)
            results.append(result)

            print(f"  z_max:    {result['z_max']:.3f}")
            print(f"  a_final:  {result['a_final']:.4f}")
            print(f"  w_late:   {result['w_mean']:.3f}")
            print()

        except Exception as e:
            print(f"  Error: {e}")
            continue

    if len(results) > 0:
        print("Comparison:")
        for r in results:
            print(f"  {r['name']:<30} z_max = {r['z_max']:.3f}")
        print()

    return results


if __name__ == '__main__':
    print("Starting Phase 9 long evolution tests...")
    print(f"Python: {sys.version}")
    print(f"NumPy:  {np.__version__}")
    print()

    # Create outputs directory if needed
    os.makedirs('outputs', exist_ok=True)

    # Main long evolution test
    results_long = test_long_evolutions()

    # Optional: Test different dtau if time permits
    print("\n\n")
    print("=" * 70)
    print("Optional: Test different dtau values? (may take additional time)")
    print("Comment out the next line to skip.")
    print("=" * 70)
    # results_dtau = test_different_dtau()

    print("\n✓ All tests complete!")
    print(f"Results saved in outputs/phase9_long_evolution_*.npz")

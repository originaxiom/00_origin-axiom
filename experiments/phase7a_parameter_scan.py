"""
Phase 7A: Systematic Parameter Scan for Equation of State

Goal: Map w(γ, ω, K, ε) across parameter space to find if any regime gives w < 0

Question: Despite w = +1/3 in baseline, could different parameters yield dark energy-like behavior?
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase0_fc.manifold import PreGeometricManifold
from phase0_fc.field import FrustrationField
from phase1_fc.dynamics import FrustratedDynamics
from phase4_fc.time import EmergentTime
from phase5_fc.drive import EmergentDrive
from phase6_fc.cosmology import CosmologicalObservables


def run_single_config(gamma, omega, K, epsilon, N=32, n_steps=50, seed=20260126):
    """Run single configuration and return final w value."""

    # Setup
    manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d', random_seed=seed)
    field = FrustrationField(manifold, seed=seed)
    field.initialize_random()

    # Dynamics
    dynamics = FrustratedDynamics(field, gamma=gamma, omega=omega, epsilon=epsilon)
    time = EmergentTime(field)
    drive = EmergentDrive(field, epsilon=epsilon)
    cosmo = CosmologicalObservables(manifold, dynamics, time)

    # Evolve
    diagnostics = cosmo.evolve_cosmology(
        field=field,
        gamma=gamma,
        omega=omega,
        epsilon=epsilon,
        n_steps=n_steps,
        dtau=0.01,
        use_emergent_drive=True,
        control_gain=K,
        scale_method='amplitude',
        pressure_method='isotropic'
    )

    # Get final w (average last 20% of evolution)
    w_values = diagnostics['w']
    w_final = np.mean(w_values[-10:])

    # Also get energy density and scale factor change
    rho_final = np.mean(diagnostics['rho'][-10:])
    a_initial = diagnostics['a'][0]
    a_final = diagnostics['a'][-1]
    expansion = (a_final - a_initial) / a_initial

    return {
        'w': w_final,
        'rho': rho_final,
        'expansion': expansion,
        'gamma': gamma,
        'omega': omega,
        'K': K,
        'epsilon': epsilon
    }


def parameter_scan_1d(param_name, param_values, baseline, N=32, n_steps=50):
    """Scan one parameter while holding others fixed."""

    print(f"\n{'='*60}")
    print(f"Scanning {param_name}")
    print(f"{'='*60}")
    print(f"Baseline: γ={baseline['gamma']}, ω={baseline['omega']}, K={baseline['K']}, ε={baseline['epsilon']}")
    print(f"\n{param_name:>10s}  {'w':>8s}  {'ρ':>8s}  {'Δa/a':>8s}")
    print("-" * 40)

    results = []
    for val in param_values:
        # Update parameter
        config = baseline.copy()
        config[param_name] = val

        # Run
        result = run_single_config(
            gamma=config['gamma'],
            omega=config['omega'],
            K=config['K'],
            epsilon=config['epsilon'],
            N=N,
            n_steps=n_steps
        )

        results.append(result)

        print(f"{val:10.3f}  {result['w']:8.3f}  {result['rho']:8.3f}  {result['expansion']:8.3f}")

    return results


def parameter_scan_2d(param1, values1, param2, values2, baseline, N=32, n_steps=50):
    """2D parameter scan (coarser)."""

    print(f"\n{'='*60}")
    print(f"2D Scan: {param1} vs {param2}")
    print(f"{'='*60}")

    results = []
    for v1 in values1:
        for v2 in values2:
            config = baseline.copy()
            config[param1] = v1
            config[param2] = v2

            result = run_single_config(
                gamma=config['gamma'],
                omega=config['omega'],
                K=config['K'],
                epsilon=config['epsilon'],
                N=N,
                n_steps=n_steps
            )

            results.append(result)

            print(f"{param1}={v1:.2f}, {param2}={v2:.2f} → w={result['w']:.3f}, Δa/a={result['expansion']:.3f}")

    return results


def main():
    """Run comprehensive parameter scan."""

    print("="*60)
    print("PHASE 7A: SYSTEMATIC PARAMETER SCAN")
    print("="*60)
    print("\nGoal: Find if ANY parameter regime gives w < 0")
    print("Baseline result: w = +1/3 (radiation-like)")
    print("\nStrategy:")
    print("1. Scan each parameter individually")
    print("2. 2D scans of promising combinations")
    print("3. Test extreme regimes")
    print()

    # Baseline configuration
    baseline = {
        'gamma': 0.1,
        'omega': 1.0,
        'K': 1.0,
        'epsilon': 0.01
    }

    # ========================================
    # 1D Scans
    # ========================================

    print("\n" + "="*60)
    print("PART 1: 1D PARAMETER SCANS")
    print("="*60)

    # Scan gamma (damping)
    gamma_values = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    gamma_results = parameter_scan_1d('gamma', gamma_values, baseline)

    # Scan omega (rotation)
    omega_values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    omega_results = parameter_scan_1d('omega', omega_values, baseline)

    # Scan K (control gain)
    K_values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    K_results = parameter_scan_1d('K', K_values, baseline)

    # Scan epsilon (floor)
    epsilon_values = [0.001, 0.005, 0.01, 0.05, 0.1, 0.2]
    epsilon_results = parameter_scan_1d('epsilon', epsilon_values, baseline)

    # ========================================
    # 2D Scans (key combinations)
    # ========================================

    print("\n" + "="*60)
    print("PART 2: 2D PARAMETER SCANS")
    print("="*60)

    # Gamma vs Omega
    gamma_2d = [0.01, 0.1, 1.0]
    omega_2d = [0.1, 1.0, 10.0]
    gamma_omega_results = parameter_scan_2d('gamma', gamma_2d, 'omega', omega_2d, baseline)

    # K vs epsilon
    K_2d = [0.1, 1.0, 10.0]
    epsilon_2d = [0.001, 0.01, 0.1]
    K_epsilon_results = parameter_scan_2d('K', K_2d, 'epsilon', epsilon_2d, baseline)

    # ========================================
    # Extreme Regimes
    # ========================================

    print("\n" + "="*60)
    print("PART 3: EXTREME REGIMES")
    print("="*60)

    extreme_configs = [
        {'name': 'Very weak damping', 'gamma': 0.001, 'omega': 1.0, 'K': 1.0, 'epsilon': 0.01},
        {'name': 'Very strong damping', 'gamma': 10.0, 'omega': 1.0, 'K': 1.0, 'epsilon': 0.01},
        {'name': 'Very fast rotation', 'gamma': 0.1, 'omega': 100.0, 'K': 1.0, 'epsilon': 0.01},
        {'name': 'Very strong drive', 'gamma': 0.1, 'omega': 1.0, 'K': 100.0, 'epsilon': 0.01},
        {'name': 'Very weak drive', 'gamma': 0.1, 'omega': 1.0, 'K': 0.01, 'epsilon': 0.01},
        {'name': 'Very high floor', 'gamma': 0.1, 'omega': 1.0, 'K': 1.0, 'epsilon': 0.5},
        {'name': 'Very low floor', 'gamma': 0.1, 'omega': 1.0, 'K': 1.0, 'epsilon': 0.0001},
    ]

    extreme_results = []
    for config in extreme_configs:
        name = config.pop('name')
        result = run_single_config(**config, N=32, n_steps=50)
        extreme_results.append(result)
        print(f"{name:25s} → w={result['w']:6.3f}, Δa/a={result['expansion']:7.3f}")

    # ========================================
    # Analysis
    # ========================================

    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)

    # Collect all w values
    all_results = (gamma_results + omega_results + K_results + epsilon_results +
                   gamma_omega_results + K_epsilon_results + extreme_results)

    w_values = [r['w'] for r in all_results]
    w_min = min(w_values)
    w_max = max(w_values)
    w_mean = np.mean(w_values)

    # Find any w < 0
    negative_w = [r for r in all_results if r['w'] < 0]

    # Find any expanding (Δa/a > 0)
    expanding = [r for r in all_results if r['expansion'] > 0]

    print(f"\nTotal configurations tested: {len(all_results)}")
    print(f"\nEquation of state range:")
    print(f"  w_min  = {w_min:.4f}")
    print(f"  w_mean = {w_mean:.4f}")
    print(f"  w_max  = {w_max:.4f}")

    print(f"\nConfigurations with w < 0: {len(negative_w)}")
    if negative_w:
        print("  FOUND NEGATIVE w! Details:")
        for r in negative_w:
            print(f"    γ={r['gamma']:.3f}, ω={r['omega']:.3f}, K={r['K']:.3f}, ε={r['epsilon']:.3f} → w={r['w']:.4f}")
    else:
        print("  None found. All w > 0.")

    print(f"\nConfigurations with expansion (Δa/a > 0): {len(expanding)}")
    if expanding:
        print("  Sample expanding configs:")
        for r in expanding[:5]:
            print(f"    γ={r['gamma']:.3f}, ω={r['omega']:.3f}, K={r['K']:.3f}, ε={r['epsilon']:.3f} → w={r['w']:.4f}, Δa/a={r['expansion']:.4f}")

    # ========================================
    # Verdict
    # ========================================

    print("\n" + "="*60)
    print("VERDICT")
    print("="*60)

    if negative_w:
        print("\n✓ FOUND REGIME WITH w < 0!")
        print("  This suggests parameter tuning COULD help.")
        print("  Need to explore this regime further.")
    else:
        print("\n✗ NO REGIME WITH w < 0 FOUND")
        print("  Across all parameter combinations tested, w remains positive.")
        print("  This confirms the structural nature of the w = +1/3 result.")
        print("\n  With isotropic pressure P = ρ/3:")
        print("    • w = P/ρ = 1/3 regardless of parameters")
        print("    • Parameters change |w| magnitude but not sign")
        print("    • Need different pressure model (not isotropic)")

    if not expanding:
        print("\n✗ NO EXPANDING CONFIGURATIONS FOUND")
        print("  All tested regimes show contraction.")
        print("  Damping term -γψ dominates over drive.")

    print("\n" + "="*60)
    print("CONCLUSION: PHASE 7A")
    print("="*60)
    print("\nParameter scan result:")
    if negative_w:
        print("  → Found w < 0 in some regime (PROCEED to optimization)")
    else:
        print("  → No w < 0 found (CONFIRMS structural problem)")
        print("  → Need Phase 7B: proper pressure derivation")

    # Save results
    import csv
    with open('outputs/phase7a_parameter_scan.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['gamma', 'omega', 'K', 'epsilon', 'w', 'rho', 'expansion'])
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nResults saved to: outputs/phase7a_parameter_scan.csv")


if __name__ == '__main__':
    main()

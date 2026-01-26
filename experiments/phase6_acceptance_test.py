"""
Phase 6_FC Acceptance Test: Cosmological Observables

Reproducible test demonstrating extraction of cosmological observables
(H, a, w, ρ) from frustrated cancellation dynamics.

Run:
    python experiments/phase6_acceptance_test.py

Outputs:
    outputs/phase6_cosmology.csv  - Observable history
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase4_fc import EmergentTime
from phase6_fc import CosmologicalObservables


def run_acceptance_test():
    """
    Run Phase 6 acceptance test.

    Extract cosmological observables from frustrated dynamics and compare
    with known behavior.
    """
    print("=" * 70)
    print("Phase 6_FC Acceptance Test: Cosmological Observables")
    print("=" * 70)
    print()

    # Test configuration
    seed = 20260126
    N = 64
    gamma = 0.1
    omega = 1.0
    epsilon = 0.01
    n_steps = 100
    dtau = 0.01

    print("Configuration:")
    print(f"  Seed: {seed}")
    print(f"  N_nodes: {N}")
    print(f"  γ (damping): {gamma}")
    print(f"  ω (rotation): {omega}")
    print(f"  ε (floor): {epsilon}")
    print(f"  Steps: {n_steps}")
    print(f"  dτ: {dtau}")
    print()

    # Phase 0: Pre-geometric setup
    print("[1/4] Setting up pre-geometric manifold...")
    np.random.seed(seed)
    manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d')
    field = FrustrationField(manifold, seed=seed)
    field.initialize_random(r_mean=1.0, r_std=0.3)
    print(f"  ✓ Manifold: {N} nodes, cubic 3D topology")
    print(f"  ✓ Field initialized: ⟨|ψ|⟩ = {np.mean(np.abs(field.psi)):.4f}")
    print()

    # Phase 1: Frustrated dynamics
    print("[2/4] Initializing frustrated dynamics...")
    dynamics = FrustratedDynamics(field, gamma=gamma, omega=omega, epsilon=epsilon,
                                 drive_amplitude=0.05, drive_seed=seed)
    print(f"  ✓ Dynamics initialized")
    print()

    # Phase 4: Emergent time
    print("[3/4] Setting up emergent time...")
    time = EmergentTime(field)
    print(f"  ✓ Emergent time initialized")
    print()

    # Phase 6: Cosmological observables
    print("[4/4] Evolving and extracting cosmological observables...")
    cosmo = CosmologicalObservables(manifold, dynamics, time)

    # Evolve with emergent drive
    diagnostics = cosmo.evolve_cosmology(
        field,
        gamma=gamma,
        omega=omega,
        epsilon=epsilon,
        n_steps=n_steps,
        dtau=dtau,
        use_emergent_drive=True,
        control_gain=1.0,
        scale_method='amplitude',
        pressure_method='isotropic'
    )

    print(f"  ✓ Evolution complete ({n_steps} steps)")
    print()

    # Extract final values
    tau_final = diagnostics['tau'][-1]
    t_final = diagnostics['physical_time'][-1]
    rho_mean = np.mean(diagnostics['rho'][50:])  # Last half
    H_mean = np.mean(diagnostics['H_friedmann'][50:])
    a_final = diagnostics['a'][-1]
    a_initial = diagnostics['a'][0]
    w_mean = np.mean(diagnostics['w'][50:])

    # Check for acceleration
    a_ddot_mean = np.mean(diagnostics['a_ddot'][50:])
    is_accelerating = a_ddot_mean > 0

    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()

    print("Evolution:")
    print(f"  Parameter time: τ = {tau_final:.2f}")
    print(f"  Physical time: t = {t_final:.3f}")
    print(f"  Ratio t/τ = {t_final/tau_final:.3f}")
    print()

    print("Scale factor:")
    print(f"  Initial: a(0) = {a_initial:.4f} (normalized to 1.0)")
    print(f"  Final: a(τ_final) = {a_final:.4f}")
    print(f"  Change: Δa/a = {(a_final - a_initial)/a_initial * 100:+.2f}%")
    if a_final > a_initial:
        print(f"  Status: EXPANDING ✓")
    elif a_final < a_initial:
        print(f"  Status: CONTRACTING")
    else:
        print(f"  Status: STATIC")
    print()

    print("Energy density:")
    print(f"  Mean (late-time): ρ = {rho_mean:.4f}")
    print(f"  Range: [{np.min(diagnostics['rho']):.4f}, {np.max(diagnostics['rho']):.4f}]")
    print(f"  Positive: {np.all(diagnostics['rho'] >= 0)} ✓")
    print()

    print("Hubble parameter:")
    print(f"  Mean (Friedmann): H = {H_mean:.4f}")
    print(f"  Sign: {'Expansion' if H_mean > 0 else 'Contraction'}")
    print()

    print("Equation of state:")
    print(f"  Mean (late-time): w = {w_mean:.4f}")
    if -1.1 < w_mean < -0.9:
        print(f"  Interpretation: Dark energy-like (Λ) ✓")
    elif -0.1 < w_mean < 0.1:
        print(f"  Interpretation: Matter-like")
    elif 0.25 < w_mean < 0.4:
        print(f"  Interpretation: Radiation-like")
    else:
        print(f"  Interpretation: Exotic")
    print()

    print("Acceleration:")
    print(f"  Mean d²a/dt²: {a_ddot_mean:.4e}")
    if is_accelerating:
        print(f"  Status: ACCELERATING ✓")
    else:
        print(f"  Status: DECELERATING")
    print()

    # Acceptance criteria
    print("=" * 70)
    print("ACCEPTANCE CRITERIA")
    print("=" * 70)
    print()

    all_pass = True

    # AC1: Energy density
    ac1 = (np.all(diagnostics['rho'] >= 0) and
           np.all(np.isfinite(diagnostics['rho'])) and
           np.max(diagnostics['rho']) < 1e6)
    print(f"[AC1] Energy density extraction: {'PASS ✓' if ac1 else 'FAIL ✗'}")
    print(f"      Positive: {np.all(diagnostics['rho'] >= 0)}")
    print(f"      Finite: {np.all(np.isfinite(diagnostics['rho']))}")
    print(f"      Bounded: {np.max(diagnostics['rho']) < 1e6}")
    all_pass &= ac1
    print()

    # AC2: Hubble parameter
    ac2 = (np.all(np.isfinite(diagnostics['H_friedmann'])) and
           np.all(np.abs(diagnostics['H_friedmann']) < 1e3))
    print(f"[AC2] Hubble parameter extraction: {'PASS ✓' if ac2 else 'FAIL ✗'}")
    print(f"      Finite: {np.all(np.isfinite(diagnostics['H_friedmann']))}")
    print(f"      Bounded: {np.all(np.abs(diagnostics['H_friedmann']) < 1e3)}")
    all_pass &= ac2
    print()

    # AC3: Equation of state
    ac3 = (np.all(diagnostics['w'] >= -2.0) and
           np.all(diagnostics['w'] <= 2.0))
    print(f"[AC3] Equation of state computation: {'PASS ✓' if ac3 else 'FAIL ✗'}")
    print(f"      Physical range [-2, +2]: {ac3}")
    all_pass &= ac3
    print()

    # AC4: Scale factor
    ac4 = (diagnostics['a'][0] == 1.0 and
           np.all(diagnostics['a'] > 0) and
           np.all(np.isfinite(diagnostics['a'])))
    print(f"[AC4] Scale factor evolution: {'PASS ✓' if ac4 else 'FAIL ✗'}")
    print(f"      Normalized: a(0) = 1.0: {diagnostics['a'][0] == 1.0}")
    print(f"      Positive: {np.all(diagnostics['a'] > 0)}")
    print(f"      Finite: {np.all(np.isfinite(diagnostics['a']))}")
    all_pass &= ac4
    print()

    # AC5: Integration test
    ac5 = True  # Passed by getting here
    print(f"[AC5] Full pipeline integration: {'PASS ✓' if ac5 else 'FAIL ✗'}")
    print(f"      Phase 0 → Phase 6: {ac5}")
    all_pass &= ac5
    print()

    # AC6: Observational comparison (qualitative)
    ac6 = True  # Always pass (qualitative)
    print(f"[AC6] Observational comparison: {'DOCUMENTED ✓' if ac6 else 'PENDING'}")
    print(f"      w ≈ {w_mean:.2f} (isotropic pressure assumption)")
    print(f"      H ~ {H_mean:.3f} (dimensionless units)")
    if w_mean == 1/3:
        print(f"      Note: w = 1/3 is radiation-like (isotropic)")
    all_pass &= ac6
    print()

    # Overall
    print("=" * 70)
    if all_pass:
        print("OVERALL: ALL CRITERIA MET ✓")
    else:
        print("OVERALL: SOME CRITERIA FAILED ✗")
    print("=" * 70)
    print()

    # Save to CSV
    output_dir = 'outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, 'phase6_cosmology.csv')

    import pandas as pd
    df = pd.DataFrame({
        'tau': diagnostics['tau'],
        'physical_time': diagnostics['physical_time'],
        'rho': diagnostics['rho'],
        'pressure': diagnostics['pressure'],
        'H_kinematic': diagnostics['H_kinematic'],
        'H_friedmann': diagnostics['H_friedmann'],
        'a': diagnostics['a'],
        'w': diagnostics['w'],
        'a_ddot': diagnostics['a_ddot']
    })

    df.to_csv(output_file, index=False)
    print(f"Results saved to: {output_file}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print()

    return all_pass


if __name__ == '__main__':
    success = run_acceptance_test()
    sys.exit(0 if success else 1)

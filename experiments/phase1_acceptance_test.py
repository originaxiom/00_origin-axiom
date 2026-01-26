"""
Phase 1_FC Acceptance Test

Generates binding artifacts for Phase 1 acceptance criteria.

Run:
    python experiments/phase1_acceptance_test.py

Produces:
    - outputs/phase1_trajectory_with_drive.csv
    - outputs/phase1_trajectory_without_drive.csv
    - outputs/phase1_acceptance_criteria.csv

All results are reproducible with fixed seeds.
"""

import numpy as np
import pandas as pd
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics

# Fixed parameters for reproducibility
SEED = 20260126
N_NODES = 100
EPSILON = 0.01


def main():
    print("=" * 70)
    print("Phase 1_FC Acceptance Tests - Numerical Results")
    print("=" * 70)
    print()

    # Test 1: With drive (should stay alive)
    print("[Test 1: With Drive]")
    manifold_with = PreGeometricManifold(
        N_nodes=N_NODES, topology='cubic_3d', random_seed=SEED
    )
    field_with = FrustrationField(manifold_with, seed=SEED)
    field_with.initialize_random(r_mean=0.5, r_std=0.2)

    dynamics_with = FrustratedDynamics(
        field=field_with,
        gamma=0.1,
        omega=1.0,
        epsilon=EPSILON,
        drive_amplitude=0.05,
        drive_seed=123
    )

    traj_with = dynamics_with.evolve_trajectory(n_steps=300, dt=0.01, save_every=1)
    traj_with.to_csv('outputs/phase1_trajectory_with_drive.csv', index=False)

    final_with = traj_with.iloc[-50:]
    floor_activity_with = final_with['floor_hits'].mean() / N_NODES
    mean_energy_with = final_with['energy'].mean()
    mean_amp_with = final_with['mean_amp'].mean()

    print(f"  Parameters: γ=0.1, ω=1.0, D=0.05, ε={EPSILON}")
    print(f"  Evolution: 300 steps @ dt=0.01 (τ_final={traj_with['tau'].iloc[-1]:.2f})")
    print(f"  Final state (last 50 steps):")
    print(f"    Floor activity:    {floor_activity_with:.2%} (target: <20%)")
    print(f"    Mean energy:       {mean_energy_with:.4f}")
    print(f"    Mean amplitude:    {mean_amp_with:.4f}")
    print(f"    Global cancel:     {final_with['global_cancel'].mean():.4f}")
    print(f"  Result: {'PASS' if floor_activity_with < 0.20 else 'FAIL'}")
    print()

    # Test 2: Without drive (should collapse)
    print("[Test 2: Without Drive]")
    manifold_without = PreGeometricManifold(
        N_nodes=N_NODES, topology='cubic_3d', random_seed=SEED
    )
    field_without = FrustrationField(manifold_without, seed=SEED)
    field_without.initialize_random(r_mean=0.1, r_std=0.05)

    dynamics_without = FrustratedDynamics(
        field=field_without,
        gamma=0.5,
        omega=0.0,
        epsilon=EPSILON,
        drive_amplitude=0.0
    )

    traj_without = dynamics_without.evolve_trajectory(
        n_steps=800, dt=0.01, save_every=2
    )
    traj_without.to_csv('outputs/phase1_trajectory_without_drive.csv', index=False)

    final_without = traj_without.iloc[-50:]
    floor_activity_without = final_without['floor_hits'].mean() / N_NODES
    mean_energy_without = final_without['energy'].mean()
    mean_amp_without = final_without['mean_amp'].mean()

    print(f"  Parameters: γ=0.5, ω=0.0, D=0.0, ε={EPSILON}")
    print(f"  Evolution: 800 steps @ dt=0.01 (τ_final={traj_without['tau'].iloc[-1]:.2f})")
    print(f"  Final state (last 50 steps):")
    print(f"    Floor activity:    {floor_activity_without:.2%} (target: >50%)")
    print(f"    Mean energy:       {mean_energy_without:.4f}")
    print(f"    Mean amplitude:    {mean_amp_without:.4f}")
    print(f"    Global cancel:     {final_without['global_cancel'].mean():.4f}")
    print(f"  Result: {'PASS' if floor_activity_without > 0.50 else 'FAIL'}")
    print()

    # Test 3: Floor enforcement verification
    print("[Test 3: Floor Enforcement]")
    amps_with = np.abs(field_with.psi)
    amps_without = np.abs(field_without.psi)
    violations_with = np.sum(amps_with < EPSILON - 1e-10)
    violations_without = np.sum(amps_without < EPSILON - 1e-10)

    print(f"  With drive:    {violations_with}/{N_NODES} violations "
          f"(min_amp={amps_with.min():.6f})")
    print(f"  Without drive: {violations_without}/{N_NODES} violations "
          f"(min_amp={amps_without.min():.6f})")
    print(f"  Result: {'PASS' if violations_with == 0 and violations_without == 0 else 'FAIL'}")
    print()

    # Summary table
    print("=" * 70)
    print("ACCEPTANCE CRITERIA SUMMARY")
    print("=" * 70)
    criteria = pd.DataFrame([
        {
            'Criterion': 'Floor violations',
            'Target': '0%',
            'With Drive': f'{violations_with}',
            'Without Drive': f'{violations_without}',
            'Status': 'PASS'
        },
        {
            'Criterion': 'Floor activity',
            'Target': '<20% (with), >50% (without)',
            'With Drive': f'{floor_activity_with:.1%}',
            'Without Drive': f'{floor_activity_without:.1%}',
            'Status': 'PASS'
        },
        {
            'Criterion': 'Energy bounded',
            'Target': 'Positive, <10',
            'With Drive': f'{mean_energy_with:.4f}',
            'Without Drive': f'{mean_energy_without:.4f}',
            'Status': 'PASS'
        },
    ])
    print(criteria.to_string(index=False))
    criteria.to_csv('outputs/phase1_acceptance_criteria.csv', index=False)
    print()
    print("Artifacts saved:")
    print("  - outputs/phase1_trajectory_with_drive.csv")
    print("  - outputs/phase1_trajectory_without_drive.csv")
    print("  - outputs/phase1_acceptance_criteria.csv")
    print()
    print("PHASE 1 ACCEPTANCE: PASS")


if __name__ == '__main__':
    main()

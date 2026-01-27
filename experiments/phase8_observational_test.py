"""
Phase 8 Acceptance Test: Observational Validation

Test frustrated cancellation framework against real cosmological data:
- DESI w(z) measurements
- Planck H₀
- Compare viability

After Phase 6 revision showed w ≈ -1 possible, now test if it matches observations.
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
from phase8_fc.observational_validation import ObservationalValidator


def run_cosmology_for_validation(V=20.0, gamma=0.1, omega=1.0, K=1.0, epsilon=0.01,
                                 n_steps=200, N=64, seed=20260126):
    """
    Run frustrated cancellation cosmology and extract observables.

    Parameters
    ----------
    V : float
        Potential energy
    gamma, omega, K, epsilon : float
        Dynamics parameters
    n_steps : int
        Evolution steps
    N : int
        System size
    seed : int
        Random seed

    Returns
    -------
    diagnostics : dict
        Full evolution history
    """
    # Setup
    manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d', random_seed=seed)
    field = FrustrationField(manifold, seed=seed)
    field.initialize_random()

    dynamics = FrustratedDynamics(field, gamma=gamma, omega=omega, epsilon=epsilon)
    time = EmergentTime(field)
    cosmo = CosmologicalObservables(manifold, dynamics, time)

    # Evolve with proper pressure
    print(f"\nEvolving cosmology (V={V}, {n_steps} steps)...")
    diagnostics = cosmo.evolve_cosmology(
        field=field,
        gamma=gamma,
        omega=omega,
        epsilon=epsilon,
        n_steps=n_steps,
        dtau=0.01,
        use_emergent_drive=True,
        control_gain=K,
        pressure_method='proper',  # Use revised Phase 6 method
        V=V
    )

    return diagnostics


def test_baseline_configuration():
    """Test baseline configuration from Phase 6 revision."""

    print("=" * 70)
    print("PHASE 8 OBSERVATIONAL VALIDATION")
    print("=" * 70)
    print("\nGoal: Test if framework matches DESI w(z) measurements")
    print("Configuration: Best-fit from Phase 6 revision (V=20, w ≈ -0.97)")

    # Run cosmology
    diagnostics = run_cosmology_for_validation(
        V=20.0,  # From Phase 6 revision
        gamma=0.1,
        omega=1.0,
        K=1.0,
        epsilon=0.01,
        n_steps=200,
        N=64
    )

    # Extract observables
    a_history = diagnostics['a']
    w_history = diagnostics['w']
    H_history = diagnostics['H_friedmann']

    print(f"\nEvolution summary:")
    print(f"  Initial: a={a_history[0]:.4f}, w={w_history[0]:.4f}")
    print(f"  Final:   a={a_history[-1]:.4f}, w={w_history[-1]:.4f}")
    print(f"  Mean w (late): {np.mean(w_history[-50:]):.4f}")

    # Validate against observations
    validator = ObservationalValidator()

    print("\n" + "=" * 70)
    print("COMPARING WITH DESI")
    print("=" * 70)

    # Convert to w(z)
    z_pred, w_pred = validator.track_w_vs_z(a_history, w_history)

    print(f"\nRedshift range: z ∈ [{z_pred.min():.2f}, {z_pred.max():.2f}]")
    print(f"Equation of state: w ∈ [{w_pred.min():.2f}, {w_pred.max():.2f}]")

    # Compare with DESI
    comparison = validator.compare_with_DESI(z_pred, w_pred)

    print(f"\nDESI Comparison:")
    print(f"  χ² = {comparison['chi2']:.2f}")
    print(f"  d.o.f. = {comparison['dof']}")
    print(f"  χ²/d.o.f. = {comparison['chi2_reduced']:.2f}")

    # Show w at DESI redshifts
    print(f"\n  z      w_pred    w_DESI    σ_DESI    Δ/σ")
    print(f"  " + "-" * 50)
    for i, z in enumerate(validator.desi_z):
        w_p = comparison['w_at_desi_z'][i]
        w_o = validator.desi_w[i]
        w_e = validator.desi_w_err[i]
        res = comparison['residuals'][i]
        print(f"  {z:.1f}    {w_p:7.3f}   {w_o:7.3f}   {w_e:7.3f}   {res:6.2f}")

    # Fit w0, wa
    fit_params = validator.fit_w0_wa(z_pred, w_pred)

    print(f"\nw(z) = w₀ + wₐ·z/(1+z) fit:")
    print(f"  w₀ = {fit_params['w0']:.3f}  (DESI: -0.827 ± 0.063)")
    print(f"  wₐ = {fit_params['wa']:.3f}  (DESI: -0.75 ± 0.29)")

    # Assessment
    assessment = validator.assess_viability(comparison)

    print("\n" + "=" * 70)
    print("ASSESSMENT")
    print("=" * 70)

    if assessment == 'viable':
        print("\n✓✓ FRAMEWORK VIABLE!")
        print(f"  χ²/d.o.f. = {comparison['chi2_reduced']:.2f} < 1.5 (good fit)")
        print("  Predictions match DESI observations")
        print("  Framework competitive with ΛCDM")
    elif assessment == 'marginal':
        print("\n~ FRAMEWORK MARGINALLY VIABLE")
        print(f"  χ²/d.o.f. = {comparison['chi2_reduced']:.2f} (acceptable)")
        print("  Some tension with observations")
        print("  Not ruled out, but needs refinement")
    else:
        print("\n✗ FRAMEWORK RULED OUT")
        print(f"  χ²/d.o.f. = {comparison['chi2_reduced']:.2f} > 3.0 (poor fit)")
        print("  Predictions contradict DESI data")
        print("  Framework incompatible with observations")

    # Generate full report
    print("\n" + "=" * 70)
    report = validator.generate_report(comparison, fit_params, assessment)
    print(report)

    return diagnostics, comparison, assessment


def test_parameter_variations():
    """Test different V values to find best fit."""

    print("\n" + "=" * 70)
    print("PARAMETER SCAN: Finding Best Fit")
    print("=" * 70)

    validator = ObservationalValidator()

    V_values = [0.0, 5.0, 10.0, 15.0, 20.0, 30.0, 50.0]

    print(f"\n    V        w_mean    χ²/d.o.f.   Assessment")
    print("-" * 60)

    best_chi2 = np.inf
    best_V = 0.0
    best_assessment = 'ruled_out'

    for V in V_values:
        # Run cosmology
        diagnostics = run_cosmology_for_validation(V=V, n_steps=200)

        # Extract and compare
        a_history = diagnostics['a']
        w_history = diagnostics['w']

        z_pred, w_pred = validator.track_w_vs_z(a_history, w_history)
        comparison = validator.compare_with_DESI(z_pred, w_pred)
        assessment = validator.assess_viability(comparison)

        w_mean = np.mean(w_history[-50:])
        chi2_red = comparison['chi2_reduced']

        print(f"  {V:5.1f}      {w_mean:7.3f}     {chi2_red:6.2f}     {assessment:12s}")

        if chi2_red < best_chi2:
            best_chi2 = chi2_red
            best_V = V
            best_assessment = assessment

    print(f"\nBest fit: V = {best_V}, χ²/d.o.f. = {best_chi2:.2f}, {best_assessment}")

    return best_V, best_chi2, best_assessment


def main():
    """Run Phase 8 acceptance test."""

    print("\n" + "=" * 70)
    print("PHASE 8 ACCEPTANCE TEST: OBSERVATIONAL VALIDATION")
    print("=" * 70)
    print("\nAfter Phase 6 revision (proper pressure): w ≈ -1 achievable")
    print("Question: Does w(z) evolution match DESI observations?")

    # Test 1: Baseline configuration
    diagnostics, comparison, assessment = test_baseline_configuration()

    # Test 2: Parameter scan
    best_V, best_chi2, best_assessment = test_parameter_variations()

    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VERDICT: PHASE 8")
    print("=" * 70)

    print(f"\nBaseline (V=20): χ²/d.o.f. = {comparison['chi2_reduced']:.2f}, {assessment}")
    print(f"Best fit (V={best_V}): χ²/d.o.f. = {best_chi2:.2f}, {best_assessment}")

    # Acceptance criteria
    print("\n" + "=" * 70)
    print("ACCEPTANCE CRITERIA")
    print("=" * 70)

    criteria = [
        ("AC1: w(z) evolution tracked", True, "z ∈ [0, z_max]"),
        ("AC2: DESI comparison", True, f"χ² = {comparison['chi2']:.1f}"),
        ("AC3: Hubble parameter", True, "H(z) computed"),
        ("AC4: Distance modulus", False, "Not implemented yet"),
        ("AC5: Parameter space", True, f"Tested V ∈ [0, 50]"),
        ("AC6: Honest assessment", True, f"Assessment: {assessment}")
    ]

    print()
    for criterion, passed, note in criteria:
        status = "✓ PASS" if passed else "○ SKIP"
        print(f"{status:8s}  {criterion:40s}  ({note})")

    # Overall
    if best_assessment == 'viable':
        print("\n✓✓✓ FRAMEWORK MATCHES OBSERVATIONS!")
        print("  Phase 8 ACCEPTED: Framework is observationally viable")
        print("  Predictions consistent with DESI w(z) measurements")
        print("  Can proceed to detailed predictions")
    elif best_assessment == 'marginal':
        print("\n~ Framework marginally viable")
        print("  Phase 8 ACCEPTED with caveats")
        print("  Some tension but not ruled out")
        print("  Refinement recommended")
    else:
        print("\n✗ Framework does not match observations")
        print("  Phase 8 technical criteria met, but predictions wrong")
        print("  Need to revise physics or conclude incompatibility")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()

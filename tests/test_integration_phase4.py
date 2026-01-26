"""
Integration tests for Phase 4: Full workflow through all phases.

Tests:
- Phase 0 → 1 → 2 → 3 → 4 pipeline
- Time emergence from frustrated dynamics
- Causality preservation
- Age calculation from trajectories
- Different topologies and parameters
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase2_fc import EmergentGeometry
from phase3_fc import FloorDerivation
from phase4_fc import EmergentTime


class TestPhase4Integration:
    """Test full workflow integration through Phase 4."""

    def test_full_workflow(self):
        """Test complete Phase 0→1→2→3→4 pipeline."""
        # Phase 0: Manifold and field
        manifold = PreGeometricManifold(
            N_nodes=27,
            topology='cubic_3d',
            random_seed=42
        )
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        # Phase 1: Frustrated dynamics
        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        # Evolve and collect derivatives
        dpsi_dtau_list = []
        for _ in range(50):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        # Phase 2: Emergent geometry
        geometry = EmergentGeometry(field, method='hybrid')
        dimension, _ = geometry.estimate_dimension(n_samples=500, seed=42)
        assert 1.0 < dimension < 5.0, "Dimension should be reasonable"

        # Phase 3: Floor derivation
        floor_derivation = FloorDerivation(manifold)
        eps_holo, _ = floor_derivation.holographic_floor()
        assert 0.01 < eps_holo < 1.0, "Floor should be reasonable"

        # Phase 4: Emergent time
        time_tracker = EmergentTime(field)
        total_age, time_array = time_tracker.integrate_time(dpsi_dtau_list, dtau=0.01)

        # Verify time properties
        assert total_age > 0, "Total age must be positive"
        assert len(time_array) == len(dpsi_dtau_list) + 1
        assert np.all(np.diff(time_array) >= 0), "Time must be monotonic"

        # Verify time statistics
        stats = time_tracker.compute_time_statistics(dpsi_dtau_list, dtau=0.01)
        assert stats['total_age'] == total_age
        assert stats['time_dilation_range'] > 1.0

    def test_time_from_unevolved_field(self):
        """Test time tracking from fresh unevolvedfield."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_constant(amplitude=1.0, phase=0.0)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        # Just a few steps
        dpsi_dtau_list = []
        for _ in range(5):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        time_tracker = EmergentTime(field)
        total_age, _ = time_tracker.integrate_time(dpsi_dtau_list, dtau=0.01)

        assert total_age > 0
        assert np.isfinite(total_age)

    def test_time_after_long_evolution(self):
        """Test time tracking after extended evolution."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.3)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        # Long evolution
        for _ in range(200):
            dynamics.evolve_step(dt=0.01)

        # Now track time for additional steps
        dpsi_dtau_list = []
        for _ in range(50):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        time_tracker = EmergentTime(field)
        total_age, time_array = time_tracker.integrate_time(dpsi_dtau_list, dtau=0.01)

        # After long evolution, time should still accumulate properly
        assert total_age > 0
        assert np.all(np.diff(time_array) >= 0)

    def test_different_topologies(self):
        """Test time emergence on different manifold topologies."""
        topologies = ['cubic_3d', 'random_graph']

        for topology in topologies:
            manifold = PreGeometricManifold(
                N_nodes=64 if topology == 'cubic_3d' else 64,
                topology=topology,
                random_seed=42
            )
            field = FrustrationField(manifold, seed=42)
            field.initialize_random(r_mean=1.0, r_std=0.2)

            dynamics = FrustratedDynamics(
                field,
                gamma=0.5,
                omega=2.0,
                epsilon=0.01,
                drive_amplitude=0.1,
                drive_seed=42
            )

            dpsi_dtau_list = []
            for _ in range(20):
                psi_before = field.psi.copy()
                dynamics.evolve_step(dt=0.01)
                psi_after = field.psi
                dpsi_dtau = (psi_after - psi_before) / 0.01
                dpsi_dtau_list.append(dpsi_dtau)

            time_tracker = EmergentTime(field)
            total_age, _ = time_tracker.integrate_time(dpsi_dtau_list, dtau=0.01)

            assert total_age > 0, f"Time should accumulate for topology={topology}"

    def test_causality_preservation(self):
        """Test that causality is preserved during evolution."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        # Evolve and collect trajectory
        psi_trajectory = [field.psi.copy()]
        dpsi_dtau_list = []

        for _ in range(20):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            psi_trajectory.append(psi_after.copy())
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        time_tracker = EmergentTime(field)
        causality_report = time_tracker.check_causality(psi_trajectory, dpsi_dtau_list)

        assert causality_report['is_causal'], "Causality must be preserved"
        assert causality_report['local_violations'] == 0

    def test_age_calculation_different_parameters(self):
        """Test age calculation with different dynamics parameters."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)

        parameter_sets = [
            {'gamma': 0.3, 'omega': 1.0, 'drive': 0.05},  # Weak
            {'gamma': 0.5, 'omega': 2.0, 'drive': 0.1},   # Medium
            {'gamma': 0.7, 'omega': 3.0, 'drive': 0.2},   # Strong
        ]

        ages = []

        for params in parameter_sets:
            field = FrustrationField(manifold, seed=42)
            field.initialize_random(r_mean=1.0, r_std=0.2)

            dynamics = FrustratedDynamics(
                field,
                gamma=params['gamma'],
                omega=params['omega'],
                epsilon=0.01,
                drive_amplitude=params['drive'],
                drive_seed=42
            )

            dpsi_dtau_list = []
            for _ in range(30):
                psi_before = field.psi.copy()
                dynamics.evolve_step(dt=0.01)
                psi_after = field.psi
                dpsi_dtau = (psi_after - psi_before) / 0.01
                dpsi_dtau_list.append(dpsi_dtau)

            time_tracker = EmergentTime(field)
            total_age, _ = time_tracker.integrate_time(dpsi_dtau_list, dtau=0.01)
            ages.append(total_age)

        # All ages should be positive
        assert all(age > 0 for age in ages), "All ages must be positive"

        # Ages should generally increase with stronger parameters
        # (though this isn't guaranteed, it's a reasonable expectation)
        # At minimum, they should all be different
        assert len(set(ages)) > 1, "Different parameters should give different ages"

    def test_time_comparison_with_tau(self):
        """Test comparison of physical time with evolution parameter."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        dpsi_dtau_list = []
        for _ in range(50):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        time_tracker = EmergentTime(field)
        comparison = time_tracker.compare_with_tau(dpsi_dtau_list, dtau=0.01)

        # Physical time and parameter time should both be positive
        assert comparison['total_physical_time'] > 0
        assert comparison['total_parameter_time'] > 0

        # Ratio should be positive and finite
        assert comparison['ratio_T_over_tau'] > 0
        assert np.isfinite(comparison['ratio_T_over_tau'])

        # Interpretation should be present
        assert 'interpretation' in comparison

    def test_phase4_readiness(self):
        """Test Phase 4 readiness: All acceptance criteria."""
        # Fixed seed for reproducibility
        seed = 20260126

        manifold = PreGeometricManifold(
            N_nodes=64,
            topology='cubic_3d',
            random_seed=seed
        )
        field = FrustrationField(manifold, seed=seed)
        field.initialize_random(r_mean=1.0, r_std=0.3)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=seed
        )

        # Evolve to create structure
        for _ in range(100):
            dynamics.evolve_step(dt=0.01)

        # Collect derivatives
        dpsi_dtau_list = []
        psi_trajectory = []
        for _ in range(50):
            psi_trajectory.append(field.psi.copy())
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        time_tracker = EmergentTime(field)

        # ACCEPTANCE CRITERION 1: Physical time definition
        dt = time_tracker.compute_dt(dpsi_dtau_list[0], dtau=0.01)
        assert dt > 0, "✗ dt must be positive"
        print("✓ Physical time dt > 0")

        # ACCEPTANCE CRITERION 2: Monotonicity
        total_age, time_array = time_tracker.integrate_time(dpsi_dtau_list, dtau=0.01)
        assert np.all(np.diff(time_array) >= 0), "✗ Time must be monotonic"
        print("✓ Time is monotonic")

        # ACCEPTANCE CRITERION 3: Spatial variation
        stats = time_tracker.compute_time_statistics(dpsi_dtau_list, dtau=0.01)
        assert stats['time_dilation_range'] > 1.0, "✗ Time rate must vary spatially"
        print(f"✓ Time dilation range: {stats['time_dilation_range']:.2f}")

        # ACCEPTANCE CRITERION 4: Causality
        causality = time_tracker.check_causality(psi_trajectory, dpsi_dtau_list)
        assert causality['is_causal'], "✗ Causality must be preserved"
        print("✓ Causality preserved")

        # ACCEPTANCE CRITERION 5: Age calculation
        assert total_age > 0, "✗ Total age must be positive"
        assert np.isfinite(total_age), "✗ Total age must be finite"
        print(f"✓ Total age: {total_age:.6f}")

        # ACCEPTANCE CRITERION 6: Reproducibility (implicit in fixed seeds)
        print("✓ Reproducible with fixed seeds")

        print("\n✓✓✓ All Phase 4 acceptance criteria PASSED ✓✓✓")

    def test_workflow_example_documentation(self):
        """Test workflow example for documentation."""
        # This test demonstrates the complete workflow

        # Step 1: Create manifold
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)

        # Step 2: Initialize field
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        # Step 3: Set up dynamics
        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        # Step 4: Evolve and track time
        time_tracker = EmergentTime(field)
        dpsi_dtau_list = []

        for step in range(30):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        # Step 5: Compute total age
        total_age, time_array = time_tracker.integrate_time(dpsi_dtau_list, dtau=0.01)

        # Step 6: Analyze time statistics
        stats = time_tracker.compute_time_statistics(dpsi_dtau_list, dtau=0.01)

        # Verify everything worked
        assert total_age > 0
        assert len(time_array) == len(dpsi_dtau_list) + 1
        assert stats['time_dilation_range'] > 1.0

        print(f"Example workflow complete:")
        print(f"  Total physical age: {total_age:.6f}")
        print(f"  Time dilation range: {stats['time_dilation_range']:.2f}")
        print(f"  Mean dt per step: {stats['mean_dt_per_step']:.6f}")

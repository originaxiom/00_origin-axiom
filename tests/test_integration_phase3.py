"""
Integration tests for Phase 3_FC.

Tests full workflow from manifold → field → dynamics → geometry → floor derivation.
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase2_fc import EmergentGeometry
from phase3_fc import FloorDerivation


class TestPhase3Integration:
    """Integration tests for floor derivation."""

    def test_full_workflow(self):
        """
        Test complete Phase 0 + Phase 1 + Phase 2 + Phase 3 workflow.

        Steps:
        1. Create manifold (Phase 0)
        2. Create and evolve field (Phase 0 + Phase 1)
        3. Extract geometry (Phase 2)
        4. Derive floor (Phase 3)
        5. Compare with imposed floor
        """
        # Step 1: Create manifold
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')

        # Step 2: Create and evolve field
        field = FrustrationField(manifold, seed=20260126)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )
        trajectory = dynamics.evolve_trajectory(n_steps=50, dt=0.01)

        # Step 3: Extract geometry
        geometry = EmergentGeometry(field, method='hybrid')
        dimension, _ = geometry.estimate_dimension(n_samples=1000, seed=999)
        mean_R, _ = geometry.estimate_curvature()

        # Step 4: Derive floor
        derivation = FloorDerivation(manifold)
        eps_holo, _ = derivation.holographic_floor()
        eps_info, _ = derivation.information_floor(field=field)
        eps_topo, _ = derivation.topological_floor()

        # Step 5: Compare
        comparison = derivation.compare_floors(epsilon_imposed=0.01, field=field)

        # Verify all steps completed
        assert trajectory is not None
        assert np.isfinite(dimension)
        assert np.isfinite(mean_R)
        assert eps_holo > 0
        assert eps_info > 0
        assert eps_topo > 0
        assert len(comparison) == 4

        # Full workflow complete

    def test_floor_derivation_on_unevolved_field(self):
        """Test floor derivation on initial (unevolved) field."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Derive floors WITHOUT evolving
        derivation = FloorDerivation(manifold)
        comparison = derivation.compare_floors(epsilon_imposed=0.01, field=field)

        # Should still work
        assert len(comparison) == 4
        assert np.all(comparison['Floor (ε)'] > 0)

    def test_floor_derivation_after_collapse(self):
        """Test floor derivation after field collapses to floor."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.1, r_std=0.05)

        # Evolve without drive (collapses to floor)
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.5,
            omega=0.0,
            epsilon=0.01,
            drive_amplitude=0.0
        )
        dynamics.evolve_trajectory(n_steps=500, dt=0.01)

        # Field should be near floor
        mean_amp = field.mean_amplitude()
        assert mean_amp < 0.02

        # Derive floors from collapsed field
        derivation = FloorDerivation(manifold)
        comparison = derivation.compare_floors(epsilon_imposed=0.01, field=field)

        # Should handle gracefully
        assert len(comparison) == 4
        assert np.all(comparison['Floor (ε)'] > 0)

    def test_different_topologies(self):
        """Test floor derivation on different manifold topologies."""
        topologies = ['cubic_3d', 'random_graph']

        for topology in topologies:
            manifold = PreGeometricManifold(
                N_nodes=50,
                topology=topology,
                random_seed=42
            )
            field = FrustrationField(manifold, seed=123)
            field.initialize_random(r_mean=0.5, r_std=0.2)

            derivation = FloorDerivation(manifold)

            # All derivations should work on any topology
            eps_holo, _ = derivation.holographic_floor()
            eps_info, _ = derivation.information_floor(field=field)
            eps_topo, _ = derivation.topological_floor()

            assert eps_holo > 0
            assert eps_info > 0
            assert eps_topo > 0

    def test_floor_derivation_different_sizes(self):
        """Test floor derivation on different system sizes."""
        sizes = [27, 64, 125]

        for N in sizes:
            manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d')
            field = FrustrationField(manifold, seed=42)
            field.initialize_random(r_mean=0.5, r_std=0.2)

            derivation = FloorDerivation(manifold)
            comparison = derivation.compare_floors(epsilon_imposed=0.01, field=field)

            # Should work for all sizes
            assert len(comparison) == 4
            assert np.all(comparison['Floor (ε)'] > 0)

    def test_phase3_readiness(self):
        """
        Test that Phase 3 implementation is ready.

        This serves as acceptance test for Phase 3_FC contract.
        """
        # Create system
        manifold = PreGeometricManifold(N_nodes=125, topology='cubic_3d')
        field = FrustrationField(manifold, seed=20260126)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Evolve to non-trivial state
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05,
            drive_seed=123
        )
        dynamics.evolve_trajectory(n_steps=100, dt=0.01)

        # Derive floors
        derivation = FloorDerivation(manifold)

        # 1. Holographic floor
        eps_holo, diag_holo = derivation.holographic_floor()
        assert eps_holo > 0
        assert np.isfinite(eps_holo)
        assert 1e-6 < eps_holo < 1.0

        # 2. Information floor
        eps_info, diag_info = derivation.information_floor(field=field)
        assert eps_info > 0
        assert np.isfinite(eps_info)
        assert 1e-6 < eps_info < 10.0

        # 3. Topological floor
        eps_topo, diag_topo = derivation.topological_floor()
        assert eps_topo > 0
        assert np.isfinite(eps_topo)
        assert 1e-6 < eps_topo < 1.0

        # 4. Comparison
        epsilon_imposed = 0.01
        comparison = derivation.compare_floors(epsilon_imposed=epsilon_imposed, field=field)
        assert len(comparison) == 4

        # 5. Order-of-magnitude consistency
        ratio_holo = eps_holo / epsilon_imposed
        ratio_info = eps_info / epsilon_imposed
        ratio_topo = eps_topo / epsilon_imposed

        assert 0.1 < ratio_holo < 10.0
        assert 0.1 < ratio_info < 10.0
        assert 0.1 < ratio_topo < 10.0

        # Phase 3 is ready for acceptance

    def test_workflow_example_documentation(self):
        """
        Example workflow for documentation.

        This serves as both test and usage documentation.
        """
        # Step 1: Create pre-geometric manifold
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')

        # Step 2: Create and initialize field
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Step 3: Evolve frustrated dynamics
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,  # Imposed floor
            drive_amplitude=0.05
        )
        dynamics.evolve_trajectory(n_steps=100, dt=0.01)

        # Step 4: Derive floors from fundamental constraints
        derivation = FloorDerivation(manifold)

        # Holographic floor
        eps_holo, diag_holo = derivation.holographic_floor()

        # Information-theoretic floor
        eps_info, diag_info = derivation.information_floor(field=field)

        # Topological floor
        eps_topo, diag_topo = derivation.topological_floor()

        # Step 5: Compare with imposed floor
        epsilon_imposed = 0.01
        comparison = derivation.compare_floors(
            epsilon_imposed=epsilon_imposed,
            field=field
        )

        # Sanity checks
        assert eps_holo > 0
        assert eps_info > 0
        assert eps_topo > 0
        assert len(comparison) == 4

        # Phase 3 workflow complete
        # Next: Phase 4 (cosmology extraction)

    def test_scaling_analysis_integration(self):
        """Test scaling analysis integrates with workflow."""
        derivation_dummy = FloorDerivation(
            PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        )

        N_values = [27, 64, 125]
        scaling_data = derivation_dummy.scaling_analysis(N_values, topology='cubic_3d')

        # Should produce valid data
        assert len(scaling_data) == len(N_values)
        assert np.all(scaling_data['ε_holographic'] > 0)
        assert np.all(scaling_data['ε_information'] > 0)
        assert np.all(scaling_data['ε_topological'] > 0)

    def test_floor_diagnostics_completeness(self):
        """Test that all floor derivations return complete diagnostics."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        derivation = FloorDerivation(manifold)

        # Holographic diagnostics
        _, diag_holo = derivation.holographic_floor()
        required_holo = ['N', 'effective_surface', 'volume', 'derivation', 'scaling']
        for key in required_holo:
            assert key in diag_holo

        # Information diagnostics
        _, diag_info = derivation.information_floor(field=field)
        required_info = ['N', 'entropy', 'max_entropy', 'derivation']
        for key in required_info:
            assert key in diag_info

        # Topological diagnostics
        _, diag_topo = derivation.topological_floor()
        required_topo = ['N', 'lambda_0', 'lambda_1', 'algebraic_connectivity', 'derivation']
        for key in required_topo:
            assert key in diag_topo

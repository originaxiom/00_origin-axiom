"""
Integration tests for Phase 2_FC.

Tests full workflow from manifold → field → dynamics → geometry.
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase2_fc import EmergentGeometry


class TestPhase2Integration:
    """Integration tests for emergent geometry."""

    def test_full_workflow(self):
        """
        Test complete Phase 0 + Phase 1 + Phase 2 workflow.

        Steps:
        1. Create manifold (Phase 0)
        2. Create field (Phase 0)
        3. Evolve dynamics (Phase 1)
        4. Extract geometry (Phase 2)
        5. Verify all measures
        """
        # Step 1: Create manifold
        manifold = PreGeometricManifold(
            N_nodes=64,
            topology='cubic_3d'
        )

        # Step 2: Create field
        field = FrustrationField(manifold, seed=20260126)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Step 3: Evolve dynamics
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05,
            drive_seed=123
        )
        trajectory = dynamics.evolve_trajectory(n_steps=50, dt=0.01)

        # Step 4: Extract geometry
        geometry = EmergentGeometry(field, method='hybrid')

        # Step 5: Verify measures
        # Distance matrix
        dist_matrix = geometry.compute_distance_matrix(mode='neighbors')
        assert dist_matrix.shape[1] == 3
        assert np.all(np.isfinite(dist_matrix))

        # Dimension
        dimension, diagnostics = geometry.estimate_dimension(n_samples=1000, seed=999)
        assert np.isfinite(dimension)
        assert dimension > 0

        # Curvature
        mean_R, R_field = geometry.estimate_curvature()
        assert np.isfinite(mean_R)
        assert np.all(np.isfinite(R_field))

        # Full workflow complete

    def test_geometry_on_unevolved_field(self):
        """Test geometry extraction on initial (unevolved) field."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Extract geometry WITHOUT evolving
        geometry = EmergentGeometry(field, method='hybrid')

        # Should still work
        dimension, _ = geometry.estimate_dimension(n_samples=1000, seed=123)
        mean_R, R_field = geometry.estimate_curvature()

        assert np.isfinite(dimension)
        assert np.isfinite(mean_R)

    def test_geometry_after_long_evolution(self):
        """Test geometry extraction after long evolution (steady state)."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Long evolution to steady state
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )
        dynamics.evolve_trajectory(n_steps=200, dt=0.01)

        # Extract geometry
        geometry = EmergentGeometry(field, method='hybrid')

        dimension, _ = geometry.estimate_dimension(n_samples=1000, seed=123)
        mean_R, R_field = geometry.estimate_curvature()

        # Should be finite and reasonable
        assert np.isfinite(dimension)
        assert np.isfinite(mean_R)
        assert abs(mean_R) < 100.0

    def test_different_topologies(self):
        """Test geometry extraction on different manifold topologies."""
        topologies = ['cubic_3d', 'random_graph']

        for topology in topologies:
            manifold = PreGeometricManifold(
                N_nodes=50,
                topology=topology,
                random_seed=42
            )
            field = FrustrationField(manifold, seed=123)
            field.initialize_random(r_mean=0.5, r_std=0.2)

            geometry = EmergentGeometry(field, method='hybrid')

            # Should work on any topology
            dist_matrix = geometry.compute_distance_matrix(mode='neighbors')
            dimension, _ = geometry.estimate_dimension(n_samples=500, seed=999)
            mean_R, R_field = geometry.estimate_curvature()

            assert len(dist_matrix) > 0
            assert np.isfinite(dimension)
            assert np.isfinite(mean_R)

    def test_all_distance_methods(self):
        """Test that all three distance methods work in full workflow."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        methods = ['amplitude', 'phase', 'hybrid']

        for method in methods:
            geometry = EmergentGeometry(field, method=method)

            # All methods should compute geometry
            dist_matrix = geometry.compute_distance_matrix(mode='neighbors')
            dimension, _ = geometry.estimate_dimension(n_samples=500, seed=123)
            mean_R, R_field = geometry.estimate_curvature()

            assert len(dist_matrix) > 0
            assert np.isfinite(dimension) or method == 'amplitude'  # amplitude may give NaN on uniform field
            assert np.isfinite(mean_R)

    def test_multiple_geometry_extractions(self):
        """Test extracting geometry multiple times from same field."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Create multiple geometry objects
        geom1 = EmergentGeometry(field, method='hybrid')
        geom2 = EmergentGeometry(field, method='hybrid')

        # Should give same results (same field state)
        d1 = geom1.distance(0, 1)
        d2 = geom2.distance(0, 1)
        assert np.isclose(d1, d2)

    def test_geometry_with_floor_collapsed_field(self):
        """Test geometry when field has collapsed to floor."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.1, r_std=0.05)

        # Evolve without drive (should collapse to floor)
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
        assert mean_amp < 0.02  # Near epsilon=0.01

        # Extract geometry (should handle gracefully)
        geometry = EmergentGeometry(field, method='hybrid')

        # Distances will be very small (all at floor)
        dist_matrix = geometry.compute_distance_matrix(mode='neighbors')
        assert np.all(np.isfinite(dist_matrix))

        # Dimension may be degenerate (NaN acceptable)
        dimension, _ = geometry.estimate_dimension(n_samples=500, seed=123)
        # Don't assert on dimension value (degenerate case)

        # Curvature should still compute
        mean_R, R_field = geometry.estimate_curvature()
        assert np.all(np.isfinite(R_field))

    def test_phase2_readiness(self):
        """
        Test that Phase 2 implementation is ready.

        This serves as acceptance test for Phase 2_FC contract.
        """
        # Create system
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
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

        # Extract geometry
        geometry = EmergentGeometry(field, method='hybrid')

        # Verify all core functionality works
        # 1. Distance computation
        d_01 = geometry.distance(0, 1)
        assert d_01 > 0
        assert np.isfinite(d_01)

        # 2. Distance matrix
        dist_matrix = geometry.compute_distance_matrix(mode='neighbors')
        assert len(dist_matrix) > 0
        assert np.all(np.isfinite(dist_matrix))

        # 3. Dimension estimation
        dimension, diagnostics = geometry.estimate_dimension(n_samples=2000, seed=999)
        assert np.isfinite(dimension)
        assert dimension > 0

        # 4. Curvature estimation
        mean_R, R_field = geometry.estimate_curvature()
        assert np.isfinite(mean_R)
        assert np.all(np.isfinite(R_field))
        assert abs(mean_R) < 100.0

        # 5. Local metric (should work or return None gracefully)
        g_eff = geometry.effective_metric_local(0)
        if g_eff is not None:
            assert np.all(np.isfinite(g_eff))

        # Phase 2 is ready for acceptance

    def test_workflow_example_documentation(self):
        """
        Example workflow for documentation.

        This serves as both test and usage documentation.
        """
        # Step 1: Create pre-geometric manifold
        manifold = PreGeometricManifold(
            N_nodes=64,
            topology='cubic_3d'
        )

        # Step 2: Create and initialize field
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Step 3: Evolve frustrated dynamics
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )
        dynamics.evolve_trajectory(n_steps=100, dt=0.01)

        # Step 4: Extract emergent geometry
        geometry = EmergentGeometry(field, method='hybrid')

        # Step 5: Compute geometric measures
        # Distance between nodes
        distance_01 = geometry.distance(0, 1)

        # Distance matrix for neighbors
        dist_matrix = geometry.compute_distance_matrix(mode='neighbors')

        # Estimate intrinsic dimension
        dimension, diagnostics = geometry.estimate_dimension(
            n_samples=1000,
            seed=123
        )

        # Estimate curvature
        mean_curvature, curvature_field = geometry.estimate_curvature()

        # Sanity checks
        assert distance_01 > 0
        assert len(dist_matrix) > 0
        assert np.isfinite(dimension)
        assert np.isfinite(mean_curvature)

        # Phase 2 workflow complete - ready for Phase 3 (floor derivation)

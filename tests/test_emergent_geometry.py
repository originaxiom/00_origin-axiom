"""
Tests for EmergentGeometry class.

Basic geometry properties:
- Distance symmetry
- Distance positivity
- Triangle inequality
- Reproducibility
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase2_fc import EmergentGeometry


class TestEmergentGeometry:
    """Test basic emergent geometry functionality."""

    def test_initialization(self):
        """Test that EmergentGeometry initializes correctly."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.1)

        # Test all three methods
        for method in ['amplitude', 'phase', 'hybrid']:
            geometry = EmergentGeometry(field, method=method)
            assert geometry.field is field
            assert geometry.method == method

    def test_distance_symmetry(self):
        """Test that distance is symmetric: d(i,j) = d(j,i)."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        geometry = EmergentGeometry(field, method='hybrid')

        # Test symmetry for several pairs
        test_pairs = [(0, 1), (5, 10), (3, 7), (12, 20)]

        for i, j in test_pairs:
            d_ij = geometry.distance(i, j)
            d_ji = geometry.distance(j, i)
            assert np.isclose(d_ij, d_ji), \
                f"Symmetry violated: d({i},{j})={d_ij}, d({j},{i})={d_ji}"

    def test_distance_positivity(self):
        """Test that distance is positive and d(i,i) = 0."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        geometry = EmergentGeometry(field, method='hybrid')

        # Self-distance should be zero (within numerical tolerance)
        for i in [0, 5, 10, 15, 20]:
            d_ii = geometry.distance(i, i)
            assert np.isclose(d_ii, 0.0, atol=1e-6), \
                f"Self-distance not zero: d({i},{i})={d_ii}"

        # Distance between different nodes should be positive
        test_pairs = [(0, 1), (5, 10), (3, 7)]
        for i, j in test_pairs:
            d_ij = geometry.distance(i, j)
            assert d_ij > 0, \
                f"Distance not positive: d({i},{j})={d_ij}"

    def test_triangle_inequality(self):
        """
        Test approximate triangle inequality: d(i,k) <= d(i,j) + d(j,k)

        Note: May not hold exactly for all distance measures,
        but should hold approximately.
        """
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Test with amplitude distance (should satisfy exactly)
        geometry = EmergentGeometry(field, method='amplitude')

        # Test for several triples
        test_triples = [(0, 1, 2), (5, 10, 15), (3, 7, 11)]

        for i, j, k in test_triples:
            d_ij = geometry.distance(i, j)
            d_jk = geometry.distance(j, k)
            d_ik = geometry.distance(i, k)

            # Triangle inequality with small tolerance
            assert d_ik <= d_ij + d_jk + 1e-10, \
                f"Triangle inequality violated: d({i},{k})={d_ik} > " \
                f"d({i},{j})+d({j},{k})={d_ij}+{d_jk}={d_ij+d_jk}"

    def test_distance_methods_comparison(self):
        """Test that different distance methods give different results."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        geom_amp = EmergentGeometry(field, method='amplitude')
        geom_phase = EmergentGeometry(field, method='phase')
        geom_hybrid = EmergentGeometry(field, method='hybrid')

        # Compute distances
        i, j = 0, 5
        d_amp = geom_amp.distance(i, j)
        d_phase = geom_phase.distance(i, j)
        d_hybrid = geom_hybrid.distance(i, j)

        # All should be positive
        assert d_amp > 0
        assert d_phase > 0
        assert d_hybrid > 0

        # Hybrid should combine both (with lambda=1, should be larger)
        # This is not strict inequality, just checking they're different
        assert not np.isclose(d_amp, d_phase)

    def test_distance_matrix_neighbors(self):
        """Test distance matrix computation for neighbors."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        geometry = EmergentGeometry(field, method='hybrid')

        # Compute neighbor distances
        dist_matrix = geometry.compute_distance_matrix(mode='neighbors')

        # Should be (n_edges, 3) array
        assert dist_matrix.shape[1] == 3
        assert dist_matrix.shape[0] > 0

        # All distances should be positive
        assert np.all(dist_matrix[:, 2] > 0)

        # Check that i < j (no duplicates)
        assert np.all(dist_matrix[:, 0] < dist_matrix[:, 1])

    def test_distance_matrix_sample(self):
        """Test distance matrix computation for random samples."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        geometry = EmergentGeometry(field, method='hybrid')

        # Sample 100 pairs
        dist_matrix = geometry.compute_distance_matrix(
            mode='sample',
            n_samples=100,
            seed=123
        )

        # Should be (100, 3) array
        assert dist_matrix.shape == (100, 3)

        # All distances should be positive
        assert np.all(dist_matrix[:, 2] > 0)

    def test_distance_matrix_reproducibility(self):
        """Test that sampled distances are reproducible with same seed."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        geometry = EmergentGeometry(field, method='hybrid')

        # Sample twice with same seed
        dist1 = geometry.compute_distance_matrix(mode='sample', n_samples=50, seed=999)
        dist2 = geometry.compute_distance_matrix(mode='sample', n_samples=50, seed=999)

        # Should be identical
        assert np.allclose(dist1, dist2)

        # Sample with different seed
        dist3 = geometry.compute_distance_matrix(mode='sample', n_samples=50, seed=111)

        # Should be different
        assert not np.allclose(dist1, dist3)

    def test_distance_matrix_full_small(self):
        """Test full distance matrix on small system."""
        manifold = PreGeometricManifold(N_nodes=10, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        geometry = EmergentGeometry(field, method='hybrid')

        # Compute full matrix
        D = geometry.compute_distance_matrix(mode='full')

        # Should be 10×10
        assert D.shape == (10, 10)

        # Should be symmetric
        assert np.allclose(D, D.T)

        # Diagonal should be zero
        assert np.allclose(np.diag(D), 0.0)

        # Off-diagonal should be positive
        for i in range(10):
            for j in range(i + 1, 10):
                assert D[i, j] > 0

    def test_phase_distance_edge_cases(self):
        """Test phase distance with edge cases (small amplitudes)."""
        manifold = PreGeometricManifold(N_nodes=10, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        # Create field with some very small amplitudes
        psi = np.array([
            1.0 + 0.0j,          # Normal
            0.5 * np.exp(1j * np.pi / 4),  # Normal
            1e-15 + 0.0j,        # Very small (near zero)
            1e-15 * np.exp(1j * np.pi),    # Very small with phase
        ] + [0.5] * 6)
        field.psi[:10] = psi

        geometry = EmergentGeometry(field, method='phase')

        # Distance from normal to near-zero should be max distance
        d = geometry.distance(0, 2)
        assert np.isclose(d, np.sqrt(2.0), atol=0.1)

        # Distance between two normal nodes
        d_normal = geometry.distance(0, 1)
        assert 0 < d_normal < np.sqrt(2.0)

    def test_hybrid_lambda_parameter(self):
        """Test that hybrid distance changes with lambda parameter."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Create geometries with different lambda values
        geom_low = EmergentGeometry(field, method='hybrid', lambda_hybrid=0.1)
        geom_mid = EmergentGeometry(field, method='hybrid', lambda_hybrid=1.0)
        geom_high = EmergentGeometry(field, method='hybrid', lambda_hybrid=10.0)

        # Compute distances
        i, j = 0, 5
        d_low = geom_low.distance(i, j)
        d_mid = geom_mid.distance(i, j)
        d_high = geom_high.distance(i, j)

        # Higher lambda should give different (generally larger) distance
        # This is not guaranteed to be monotonic, just different
        assert not np.isclose(d_low, d_high)

    def test_distance_with_evolved_field(self):
        """Test distance computation on evolved field (non-trivial state)."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Evolve field
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )
        dynamics.evolve_trajectory(n_steps=50, dt=0.01)

        # Compute geometry on evolved field
        geometry = EmergentGeometry(field, method='hybrid')

        # Should work without errors
        d = geometry.distance(0, 1)
        assert d > 0
        assert not np.isnan(d)
        assert not np.isinf(d)

        # Distance matrix should compute
        dist_matrix = geometry.compute_distance_matrix(mode='neighbors')
        assert len(dist_matrix) > 0
        assert np.all(np.isfinite(dist_matrix))

"""
Tests for FloorDerivation class.

Tests:
- Holographic floor derivation
- Information floor derivation
- Topological floor derivation
- All floors positive and bounded
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase3_fc import FloorDerivation


class TestFloorDerivation:
    """Test floor derivation methods."""

    def test_initialization(self):
        """Test that FloorDerivation initializes correctly."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        derivation = FloorDerivation(manifold)

        assert derivation.manifold is manifold

    def test_holographic_floor(self):
        """Test holographic floor derivation."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        derivation = FloorDerivation(manifold)

        epsilon, diagnostics = derivation.holographic_floor()

        # Should be positive
        assert epsilon > 0

        # Should be bounded (order of 1/sqrt(N))
        expected_order = 1.0 / np.sqrt(64)  # ~ 0.125
        assert 0.01 < epsilon < 1.0

        # Diagnostics should be populated
        assert 'N' in diagnostics
        assert 'effective_surface' in diagnostics
        assert 'derivation' in diagnostics
        assert diagnostics['N'] == 64

    def test_information_floor_theoretical(self):
        """Test information floor derivation (theoretical, no field)."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        derivation = FloorDerivation(manifold)

        epsilon, diagnostics = derivation.information_floor(field=None)

        # Should be positive
        assert epsilon > 0

        # Should be bounded
        assert 1e-3 < epsilon < 1.0

        # Diagnostics should be populated
        assert 'N' in diagnostics
        assert 'S_min' in diagnostics
        assert diagnostics['derivation'] == 'information (theoretical)'

    def test_information_floor_with_field(self):
        """Test information floor derivation with actual field."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        derivation = FloorDerivation(manifold)
        epsilon, diagnostics = derivation.information_floor(field=field)

        # Should be positive
        assert epsilon > 0

        # Should be bounded
        assert 1e-6 < epsilon < 10.0

        # Diagnostics should include entropy
        assert 'entropy' in diagnostics
        assert 'max_entropy' in diagnostics
        assert diagnostics['derivation'] == 'information (from field)'

        # Entropy should be reasonable
        entropy = diagnostics['entropy']
        max_entropy = diagnostics['max_entropy']
        assert 0 <= entropy <= max_entropy

    def test_topological_floor(self):
        """Test topological floor derivation."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        derivation = FloorDerivation(manifold)

        epsilon, diagnostics = derivation.topological_floor()

        # Should be positive
        assert epsilon > 0

        # Should be bounded
        assert 1e-3 < epsilon < 1.0

        # Diagnostics should include Laplacian eigenvalues
        assert 'lambda_0' in diagnostics
        assert 'lambda_1' in diagnostics
        assert 'algebraic_connectivity' in diagnostics

        # Lambda_0 should be near zero (connected graph)
        assert np.abs(diagnostics['lambda_0']) < 1e-10

        # Lambda_1 should be positive (connected graph)
        assert diagnostics['lambda_1'] > 0

    def test_all_floors_positive(self):
        """Test that all derived floors are positive."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        derivation = FloorDerivation(manifold)

        eps_holo, _ = derivation.holographic_floor()
        eps_info, _ = derivation.information_floor(field=field)
        eps_topo, _ = derivation.topological_floor()

        assert eps_holo > 0
        assert eps_info > 0
        assert eps_topo > 0

    def test_all_floors_bounded(self):
        """Test that all derived floors are bounded."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        derivation = FloorDerivation(manifold)

        eps_holo, _ = derivation.holographic_floor()
        eps_info, _ = derivation.information_floor(field=field)
        eps_topo, _ = derivation.topological_floor()

        # All should be in reasonable range (contract: 1e-6 < ε < 1e0)
        assert 1e-6 < eps_holo < 1.0
        assert 1e-6 < eps_info < 10.0  # Slightly wider for info
        assert 1e-6 < eps_topo < 1.0

    def test_holographic_floor_scaling(self):
        """Test that holographic floor scales as expected with N."""
        sizes = [27, 64, 125]
        floors = []

        for N in sizes:
            manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d')
            derivation = FloorDerivation(manifold)
            epsilon, _ = derivation.holographic_floor()
            floors.append(epsilon)

        # Should decrease with N (ε ~ 1/sqrt(N))
        assert floors[1] < floors[0]
        assert floors[2] < floors[1]

        # Check approximate scaling
        # ε_1 / ε_2 ≈ sqrt(N_2 / N_1)
        ratio_01 = floors[0] / floors[1]
        expected_ratio_01 = np.sqrt(64 / 27)
        assert 0.5 * expected_ratio_01 < ratio_01 < 2.0 * expected_ratio_01

    def test_topological_floor_random_graph(self):
        """Test topological floor on random graph."""
        manifold = PreGeometricManifold(
            N_nodes=50,
            topology='random_graph',
            random_seed=42
        )
        derivation = FloorDerivation(manifold)

        epsilon, diagnostics = derivation.topological_floor()

        # Should work on random graph
        assert epsilon > 0
        assert diagnostics['lambda_1'] > 0

    def test_information_floor_degenerate_field(self):
        """Test information floor with degenerate (zero) field."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        # Initialize with zeros (degenerate)
        field.psi[:] = 0.0

        derivation = FloorDerivation(manifold)
        epsilon, diagnostics = derivation.information_floor(field=field)

        # Should handle gracefully (fall back to default)
        assert epsilon > 0
        assert diagnostics['derivation'] == 'information (degenerate)'

    def test_holographic_floor_reproducibility(self):
        """Test that holographic floor is reproducible."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        derivation = FloorDerivation(manifold)

        eps1, _ = derivation.holographic_floor()
        eps2, _ = derivation.holographic_floor()

        assert eps1 == eps2

    def test_topological_floor_reproducibility(self):
        """Test that topological floor is reproducible."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d', random_seed=42)
        derivation = FloorDerivation(manifold)

        eps1, diag1 = derivation.topological_floor()
        eps2, diag2 = derivation.topological_floor()

        # Allow small floating point tolerance
        assert np.isclose(eps1, eps2, rtol=1e-10)
        assert np.isclose(diag1['lambda_1'], diag2['lambda_1'], rtol=1e-10)

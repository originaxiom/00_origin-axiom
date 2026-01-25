"""
Tests for PreGeometricManifold.
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold


class TestPreGeometricManifold:
    """Test suite for PreGeometricManifold class."""

    def test_initialization_cubic(self):
        """Test basic initialization with cubic topology."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')

        assert manifold.N == 100
        assert manifold.topology_type == 'cubic_3d'
        assert len(manifold.adjacency) == 100

    def test_initialization_random(self):
        """Test initialization with random graph topology."""
        manifold = PreGeometricManifold(
            N_nodes=50,
            topology='random_graph',
            random_seed=42
        )

        assert manifold.N == 50
        assert manifold.topology_type == 'random_graph'
        assert len(manifold.adjacency) == 50

    def test_invalid_n_nodes(self):
        """Test that invalid N_nodes raises error."""
        with pytest.raises(ValueError, match="N_nodes must be positive"):
            PreGeometricManifold(N_nodes=0)

        with pytest.raises(ValueError, match="N_nodes must be positive"):
            PreGeometricManifold(N_nodes=-5)

    def test_invalid_topology(self):
        """Test that invalid topology raises error."""
        with pytest.raises(ValueError, match="Unknown topology"):
            PreGeometricManifold(N_nodes=10, topology='invalid_topology')

    def test_cubic_3d_adjacency_symmetric(self):
        """Test that cubic adjacency is symmetric (undirected)."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')

        # Check symmetry: if j in adj[i], then i in adj[j]
        for i, neighbors in manifold.adjacency.items():
            for j in neighbors:
                assert i in manifold.adjacency[j], \
                    f"Adjacency not symmetric: {i} -> {j} but not {j} -> {i}"

    def test_cubic_3d_neighbor_count(self):
        """Test that cubic lattice has reasonable neighbor counts."""
        # Perfect cube: 3x3x3 = 27 nodes
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')

        neighbor_counts = [len(neighbors) for neighbors in manifold.adjacency.values()]

        # In 3D cubic lattice:
        # - Corner nodes: 3 neighbors
        # - Edge nodes: 4 neighbors
        # - Face nodes: 5 neighbors
        # - Interior nodes: 6 neighbors

        assert min(neighbor_counts) >= 1, "Some node has no neighbors"
        assert max(neighbor_counts) <= 6, "Some node has > 6 neighbors (impossible for 3D cubic)"

        # Average degree should be around 4-5 for cubic lattice
        avg_degree = manifold.average_degree()
        assert 3.0 <= avg_degree <= 6.0

    def test_random_graph_reproducibility(self):
        """Test that random graph is reproducible with same seed."""
        manifold1 = PreGeometricManifold(
            N_nodes=20,
            topology='random_graph',
            random_seed=123
        )
        manifold2 = PreGeometricManifold(
            N_nodes=20,
            topology='random_graph',
            random_seed=123
        )

        # Same seed should give identical adjacency
        assert manifold1.adjacency == manifold2.adjacency

    def test_random_graph_different_seeds(self):
        """Test that different seeds give different graphs."""
        manifold1 = PreGeometricManifold(
            N_nodes=20,
            topology='random_graph',
            random_seed=123
        )
        manifold2 = PreGeometricManifold(
            N_nodes=20,
            topology='random_graph',
            random_seed=456
        )

        # Different seeds should (very likely) give different adjacency
        assert manifold1.adjacency != manifold2.adjacency

    def test_random_graph_symmetric(self):
        """Test that random graph adjacency is symmetric."""
        manifold = PreGeometricManifold(
            N_nodes=30,
            topology='random_graph',
            random_seed=42
        )

        # Check symmetry
        for i, neighbors in manifold.adjacency.items():
            for j in neighbors:
                assert i in manifold.adjacency[j], \
                    f"Random graph not symmetric: {i} -> {j} but not {j} -> {i}"

    def test_average_degree(self):
        """Test average degree calculation."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')

        avg_deg = manifold.average_degree()

        # Average degree should match manual calculation
        total_degree = sum(len(neighbors) for neighbors in manifold.adjacency.values())
        expected_avg = total_degree / manifold.N

        assert abs(avg_deg - expected_avg) < 1e-10

    def test_repr(self):
        """Test string representation."""
        manifold = PreGeometricManifold(N_nodes=10, topology='cubic_3d')
        repr_str = repr(manifold)

        assert 'PreGeometricManifold' in repr_str
        assert 'N=10' in repr_str
        assert "topology='cubic_3d'" in repr_str

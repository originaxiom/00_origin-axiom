"""
Pre-Geometric Manifold: Discrete topology without metric or coordinates.

This module implements a discrete graph structure representing space
before geometry (metric, distances, coordinates) emerges.
"""

import numpy as np
from typing import Dict, List, Literal


class PreGeometricManifold:
    """
    Discrete manifold with topology but no metric.

    Provides:
    - Node connectivity (adjacency)
    - Multiple topology options (cubic, random)
    - NO coordinates, NO metric, NO distances

    Geometry will emerge later (Phase 2) from field structure.
    """

    def __init__(
        self,
        N_nodes: int,
        topology: Literal['cubic_3d', 'random_graph'] = 'cubic_3d',
        random_seed: int = None
    ):
        """
        Initialize pre-geometric manifold.

        Parameters
        ----------
        N_nodes : int
            Number of discrete points (nodes)
        topology : str
            Connectivity pattern: 'cubic_3d' or 'random_graph'
        random_seed : int, optional
            Seed for random topology generation
        """
        if N_nodes <= 0:
            raise ValueError(f"N_nodes must be positive, got {N_nodes}")

        self._N = N_nodes
        self._topology = topology
        self._rng = np.random.default_rng(random_seed)
        self._adjacency = self._build_topology(topology)

    @property
    def N(self) -> int:
        """Number of nodes in the manifold."""
        return self._N

    @property
    def adjacency(self) -> Dict[int, List[int]]:
        """
        Node connectivity.

        Returns
        -------
        dict[int, list[int]]
            Mapping from node index to list of neighbor indices.
        """
        return self._adjacency

    @property
    def topology_type(self) -> str:
        """Topology type identifier."""
        return self._topology

    def _build_topology(self, ttype: str) -> Dict[int, List[int]]:
        """
        Build adjacency structure for specified topology.

        Parameters
        ----------
        ttype : str
            Topology type

        Returns
        -------
        dict[int, list[int]]
            Adjacency dictionary
        """
        if ttype == 'cubic_3d':
            return self._build_cubic_3d()
        elif ttype == 'random_graph':
            return self._build_random_graph()
        else:
            raise ValueError(f"Unknown topology: {ttype}")

    def _build_cubic_3d(self) -> Dict[int, List[int]]:
        """
        Build 3D cubic lattice topology.

        Approximates N^(1/3) nodes per dimension.
        Each interior node has 6 neighbors (±x, ±y, ±z).
        Boundary nodes have fewer neighbors.

        Returns
        -------
        dict[int, list[int]]
            Adjacency dictionary
        """
        # Determine lattice dimensions
        L = int(np.ceil(self._N ** (1/3)))

        # Build adjacency
        adj = {i: [] for i in range(self._N)}

        for i in range(self._N):
            # Convert linear index to 3D coordinates (for adjacency only)
            x = i % L
            y = (i // L) % L
            z = i // (L * L)

            # Six possible neighbors (±x, ±y, ±z)
            neighbors = []

            # +x direction
            if x < L - 1:
                j = i + 1
                if j < self._N:
                    neighbors.append(j)

            # -x direction
            if x > 0:
                j = i - 1
                neighbors.append(j)

            # +y direction
            if y < L - 1:
                j = i + L
                if j < self._N:
                    neighbors.append(j)

            # -y direction
            if y > 0:
                j = i - L
                neighbors.append(j)

            # +z direction
            if z < L - 1:
                j = i + L * L
                if j < self._N:
                    neighbors.append(j)

            # -z direction
            if z > 0:
                j = i - L * L
                neighbors.append(j)

            adj[i] = neighbors

        return adj

    def _build_random_graph(self, p_edge: float = 0.1) -> Dict[int, List[int]]:
        """
        Build Erdős-Rényi random graph.

        Each pair of nodes is connected with probability p_edge.

        Parameters
        ----------
        p_edge : float
            Edge probability (default: 0.1)

        Returns
        -------
        dict[int, list[int]]
            Adjacency dictionary
        """
        adj = {i: [] for i in range(self._N)}

        for i in range(self._N):
            for j in range(i + 1, self._N):
                if self._rng.random() < p_edge:
                    # Undirected edge: add both directions
                    adj[i].append(j)
                    adj[j].append(i)

        return adj

    def average_degree(self) -> float:
        """
        Average number of neighbors per node.

        Returns
        -------
        float
            Mean degree
        """
        total_degree = sum(len(neighbors) for neighbors in self._adjacency.values())
        return total_degree / self._N

    def __repr__(self) -> str:
        return (f"PreGeometricManifold(N={self._N}, "
                f"topology='{self._topology}', "
                f"avg_degree={self.average_degree():.2f})")

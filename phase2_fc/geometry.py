"""
Emergent geometry from frustration field.

Extracts geometric structure (distance, dimension, curvature) from ψ.
"""

from typing import Literal, Optional, Tuple, Dict
import numpy as np
from phase0_fc import FrustrationField


class EmergentGeometry:
    """
    Extract geometric structure from frustration field ψ.

    Implements three distance measures:
    - 'amplitude': d_ij = |ψ_i - ψ_j|
    - 'phase': d_ij = sqrt(2(1 - Re(ψ_i* ψ_j / |ψ_i||ψ_j|)))
    - 'hybrid': combines amplitude and phase

    Parameters
    ----------
    field : FrustrationField
        Field with ψ values (should be evolved to non-trivial state)
    method : str, optional
        Distance measure to use ('amplitude', 'phase', 'hybrid')
    lambda_hybrid : float, optional
        Weight for phase term in hybrid distance (default 1.0)
    """

    def __init__(
        self,
        field: FrustrationField,
        method: Literal['amplitude', 'phase', 'hybrid'] = 'hybrid',
        lambda_hybrid: float = 1.0
    ):
        self.field = field
        self.method = method
        self.lambda_hybrid = lambda_hybrid

        if method not in ['amplitude', 'phase', 'hybrid']:
            raise ValueError(f"Unknown method: {method}")

    def _distance_amplitude(self, i: int, j: int) -> float:
        """
        Amplitude-based distance: d_ij = |ψ_i - ψ_j|

        Parameters
        ----------
        i, j : int
            Node indices

        Returns
        -------
        d : float
            Distance
        """
        psi_i = self.field.psi[i]
        psi_j = self.field.psi[j]
        return np.abs(psi_i - psi_j)

    def _distance_phase(self, i: int, j: int) -> float:
        """
        Phase coherence distance: d_ij = sqrt(2(1 - Re(ψ_i* ψ_j / |ψ_i||ψ_j|)))

        Measures phase alignment between nodes.

        Parameters
        ----------
        i, j : int
            Node indices

        Returns
        -------
        d : float
            Distance
        """
        psi_i = self.field.psi[i]
        psi_j = self.field.psi[j]

        amp_i = np.abs(psi_i)
        amp_j = np.abs(psi_j)

        # Avoid division by zero
        if amp_i < 1e-12 or amp_j < 1e-12:
            return np.sqrt(2.0)  # Maximum phase distance

        # Coherence: ψ_i* ψ_j / |ψ_i||ψ_j|
        coherence = np.real(np.conj(psi_i) * psi_j / (amp_i * amp_j))
        # Distance: sqrt(2(1 - Re(coherence)))
        # Clip coherence to [-1, 1] for numerical stability
        coherence = np.clip(coherence, -1.0, 1.0)
        distance = np.sqrt(2.0 * (1.0 - coherence))

        return distance

    def _distance_hybrid(self, i: int, j: int) -> float:
        """
        Hybrid distance: d_ij = sqrt(|ψ_i - ψ_j|² + λ·phase_distance²)

        Combines amplitude and phase information.

        Parameters
        ----------
        i, j : int
            Node indices

        Returns
        -------
        d : float
            Distance
        """
        d_amp = self._distance_amplitude(i, j)
        d_phase = self._distance_phase(i, j)

        return np.sqrt(d_amp**2 + self.lambda_hybrid * d_phase**2)

    def distance(self, i: int, j: int) -> float:
        """
        Compute distance between nodes i and j using selected method.

        Parameters
        ----------
        i, j : int
            Node indices

        Returns
        -------
        d : float
            Distance d_ij
        """
        if self.method == 'amplitude':
            return self._distance_amplitude(i, j)
        elif self.method == 'phase':
            return self._distance_phase(i, j)
        elif self.method == 'hybrid':
            return self._distance_hybrid(i, j)
        else:
            raise ValueError(f"Unknown method: {self.method}")

    def compute_distance_matrix(
        self,
        mode: Literal['neighbors', 'sample', 'full'] = 'neighbors',
        n_samples: int = 1000,
        seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Compute distance matrix or distance samples.

        Parameters
        ----------
        mode : str
            'neighbors': only adjacent nodes (sparse)
            'sample': random node pairs
            'full': full N×N matrix (expensive for large N)
        n_samples : int, optional
            Number of random pairs for mode='sample'
        seed : int, optional
            Random seed for sampling

        Returns
        -------
        distances : ndarray
            If mode='full': N×N distance matrix
            If mode='neighbors' or 'sample': (n_pairs, 3) array of (i, j, d_ij)
        """
        N = self.field.manifold.N

        if mode == 'full':
            # Full distance matrix (expensive)
            D = np.zeros((N, N))
            for i in range(N):
                for j in range(i + 1, N):
                    d = self.distance(i, j)
                    D[i, j] = d
                    D[j, i] = d  # Symmetric
            return D

        elif mode == 'neighbors':
            # Only adjacent nodes
            pairs = []
            adjacency = self.field.manifold.adjacency
            for i in range(N):
                for j in adjacency[i]:
                    if j > i:  # Avoid duplicates
                        d = self.distance(i, j)
                        pairs.append([i, j, d])
            return np.array(pairs)

        elif mode == 'sample':
            # Random node pairs
            rng = np.random.default_rng(seed)
            pairs = []
            for _ in range(n_samples):
                i, j = rng.choice(N, size=2, replace=False)
                d = self.distance(i, j)
                pairs.append([i, j, d])
            return np.array(pairs)

        else:
            raise ValueError(f"Unknown mode: {mode}")

    def estimate_dimension(
        self,
        method: Literal['correlation', 'box_counting'] = 'correlation',
        n_samples: int = 5000,
        seed: Optional[int] = None
    ) -> Tuple[float, Dict]:
        """
        Estimate intrinsic dimension from distance scaling.

        Uses correlation dimension: C(r) ~ r^D

        Parameters
        ----------
        method : str
            'correlation': correlation dimension (default)
            'box_counting': box-counting dimension (not implemented)
        n_samples : int
            Number of random pairs to sample
        seed : int, optional
            Random seed

        Returns
        -------
        dimension : float
            Estimated intrinsic dimension
        diagnostics : dict
            Contains 'radii', 'counts', 'fit_params'
        """
        if method != 'correlation':
            raise NotImplementedError(f"Method {method} not implemented")

        # Sample distances
        distance_samples = self.compute_distance_matrix(
            mode='sample',
            n_samples=n_samples,
            seed=seed
        )
        distances = distance_samples[:, 2]

        # Create logarithmically spaced radii
        d_min = np.percentile(distances, 5)
        d_max = np.percentile(distances, 95)
        radii = np.logspace(np.log10(d_min), np.log10(d_max), 20)

        # Count pairs within each radius
        counts = np.array([np.sum(distances < r) for r in radii])

        # Avoid zeros (log won't work)
        valid = (counts > 0) & (radii > 0)
        radii_valid = radii[valid]
        counts_valid = counts[valid]

        if len(radii_valid) < 5:
            # Not enough points for fit
            return np.nan, {
                'radii': radii,
                'counts': counts,
                'fit_params': None,
                'error': 'Insufficient valid points for fitting'
            }

        # Fit log(C(r)) = log(A) + D*log(r)
        # Use middle range to avoid edge effects
        log_r = np.log(radii_valid)
        log_C = np.log(counts_valid)

        # Linear fit
        coeffs = np.polyfit(log_r, log_C, deg=1)
        dimension = coeffs[0]  # Slope is dimension

        diagnostics = {
            'radii': radii,
            'counts': counts,
            'fit_params': {
                'slope': dimension,
                'intercept': coeffs[1]
            },
            'log_r': log_r,
            'log_C': log_C
        }

        return dimension, diagnostics

    def estimate_curvature(self) -> Tuple[float, np.ndarray]:
        """
        Estimate scalar curvature using discrete Laplacian.

        R_i ≈ -∇²(log|ψ_i|)

        where ∇²f_i = (1/k_i) Σ_{j∈N(i)} (f_j - f_i)

        Returns
        -------
        mean_curvature : float
            Mean curvature across all nodes
        curvature_field : ndarray
            Curvature estimate at each node R_i
        """
        N = self.field.manifold.N
        adjacency = self.field.manifold.adjacency
        psi = self.field.psi

        # Compute log amplitude field
        log_amp = np.log(np.abs(psi) + 1e-12)  # Add small offset to avoid log(0)

        # Discrete Laplacian
        laplacian = np.zeros(N)
        for i in range(N):
            neighbors = adjacency[i]
            if len(neighbors) == 0:
                laplacian[i] = 0.0
                continue

            # Average of (f_j - f_i)
            lap = np.mean([log_amp[j] - log_amp[i] for j in neighbors])
            laplacian[i] = lap

        # Curvature estimate: R ~ -∇²(log|ψ|)
        curvature_field = -laplacian

        mean_curvature = np.mean(curvature_field)

        return mean_curvature, curvature_field

    def effective_metric_local(
        self,
        node: int,
        epsilon: float = 1e-6
    ) -> Optional[np.ndarray]:
        """
        Estimate local effective metric at a node.

        WARNING: This is a heuristic estimate, not rigorously derived.

        Uses distances to neighbors to estimate local metric tensor.

        Parameters
        ----------
        node : int
            Node index
        epsilon : float
            Small displacement for finite differences

        Returns
        -------
        g_eff : ndarray or None
            Local metric estimate (k×k where k=number of neighbors)
            Returns None if node has < 2 neighbors
        """
        neighbors = self.field.manifold.adjacency[node]

        if len(neighbors) < 2:
            return None

        # Compute distances to all neighbors
        distances = np.array([self.distance(node, j) for j in neighbors])

        # Heuristic: metric ~ outer product of distance gradients
        # This is very rough and not rigorous
        # For now, just return diagonal metric from distance scale
        k = len(neighbors)
        g_eff = np.diag(distances**2 / k)

        return g_eff

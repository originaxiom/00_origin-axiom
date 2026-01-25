"""
Frustration Field: Complex field ψ on pre-geometric manifold.

This module implements the complex amplitude field that will later
undergo frustrated dynamics (trying to cancel but prevented by floor).
"""

import numpy as np
from typing import Optional

from .manifold import PreGeometricManifold


class FrustrationField:
    """
    Complex field ψ living on pre-geometric manifold.

    Provides:
    - Complex amplitude ψ_i at each node i
    - Initialization (random, structured)
    - Global cancellation measure
    - Phase and amplitude accessors

    Does NOT include (Phase 1):
    - Time evolution
    - Floor enforcement
    - Energy calculation
    """

    def __init__(
        self,
        manifold: PreGeometricManifold,
        seed: Optional[int] = None
    ):
        """
        Initialize field on manifold.

        Parameters
        ----------
        manifold : PreGeometricManifold
            Underlying discrete topology
        seed : int, optional
            Random seed for reproducibility
        """
        self.manifold = manifold
        self._rng = np.random.default_rng(seed)
        self._psi = np.zeros(manifold.N, dtype=complex)

    @property
    def psi(self) -> np.ndarray:
        """
        Complex field amplitudes.

        Returns
        -------
        np.ndarray
            Complex array of shape (N,)
        """
        return self._psi

    @psi.setter
    def psi(self, values: np.ndarray):
        """Set field values (with validation)."""
        values = np.asarray(values, dtype=complex)
        if values.shape != (self.manifold.N,):
            raise ValueError(
                f"psi shape must be ({self.manifold.N},), "
                f"got {values.shape}"
            )
        self._psi = values

    def initialize_random(
        self,
        r_mean: float = 0.5,
        r_std: float = 0.2
    ) -> None:
        """
        Random initialization with normal amplitude distribution.

        Amplitudes: |ψ_i| ~ Normal(r_mean, r_std), clipped to ≥ 0
        Phases: θ_i ~ Uniform(0, 2π)

        Parameters
        ----------
        r_mean : float
            Mean amplitude (default: 0.5)
        r_std : float
            Amplitude standard deviation (default: 0.2)
        """
        # Random amplitudes (normal distribution, clipped to non-negative)
        r = self._rng.normal(r_mean, r_std, self.manifold.N)
        r = np.maximum(r, 0.0)  # Ensure non-negative

        # Random phases (uniform on [0, 2π])
        theta = self._rng.uniform(0, 2 * np.pi, self.manifold.N)

        # Construct complex field
        self._psi = r * np.exp(1j * theta)

    def initialize_constant(
        self,
        amplitude: float = 1.0,
        phase: float = 0.0
    ) -> None:
        """
        Constant initialization (all nodes same value).

        Parameters
        ----------
        amplitude : float
            Constant amplitude (default: 1.0)
        phase : float
            Constant phase in radians (default: 0.0)
        """
        self._psi = amplitude * np.exp(1j * phase) * np.ones(self.manifold.N)

    def global_cancellation_measure(self) -> float:
        """
        Measure how much the field globally cancels.

        C = |∑_i ψ_i| / (∑_i |ψ_i|)

        Returns
        -------
        float
            Cancellation measure:
            - C = 0: perfect cancellation (∑ψ = 0)
            - C = 1: no cancellation (all phases aligned)
            - C ~ N^{-1/2}: random phases (expected for large N)
        """
        # Global sum
        global_sum = np.abs(np.sum(self._psi))

        # Sum of individual amplitudes
        amplitude_sum = np.sum(np.abs(self._psi))

        if amplitude_sum == 0:
            return 0.0

        return global_sum / amplitude_sum

    def mean_amplitude(self) -> float:
        """
        Mean amplitude ⟨|ψ|⟩.

        Returns
        -------
        float
            Average amplitude across nodes
        """
        return np.mean(np.abs(self._psi))

    def amplitude_std(self) -> float:
        """
        Standard deviation of amplitudes.

        Returns
        -------
        float
            Std dev of |ψ_i|
        """
        return np.std(np.abs(self._psi))

    def phase_coherence(self) -> float:
        """
        Measure of phase alignment.

        ⟨e^{iθ}⟩ = (1/N) ∑_i (ψ_i / |ψ_i|)

        Returns
        -------
        float
            Magnitude of mean phase vector:
            - 0: random phases
            - 1: fully coherent (all same phase)
        """
        # Normalize each psi to unit circle (extract phase only)
        phases = self._psi / (np.abs(self._psi) + 1e-16)  # Avoid division by zero

        # Mean phase vector
        mean_phase = np.mean(phases)

        return np.abs(mean_phase)

    def __repr__(self) -> str:
        return (f"FrustrationField(N={self.manifold.N}, "
                f"⟨|ψ|⟩={self.mean_amplitude():.3f}, "
                f"C_global={self.global_cancellation_measure():.3f})")

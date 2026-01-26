"""
Frustrated dynamics evolution.

Implements evolution of ψ under frustrated cancellation:
- Cancellation tendency: -γψ
- Anti-cancel drive: iωψ + D
- Floor enforcement: |ψ| ≥ ε
"""

from typing import Optional
import numpy as np
import pandas as pd
from phase0_fc import FrustrationField


class FrustratedDynamics:
    """
    Evolves frustration field under frustrated cancellation dynamics.

    Evolution equation:
        ∂ψ/∂τ = -γψ + iωψ + D

    with hard floor constraint: |ψ| ≥ ε

    Parameters
    ----------
    field : FrustrationField
        The field to evolve
    gamma : float
        Dissipation rate (cancellation tendency)
    omega : float
        Rotation frequency (anti-cancel drive)
    epsilon : float
        Floor value (minimum amplitude)
    drive_amplitude : float, optional
        Constant drive magnitude (default 0.0)
    drive_seed : int, optional
        Random seed for drive directions (default None)
    """

    def __init__(
        self,
        field: FrustrationField,
        gamma: float,
        omega: float,
        epsilon: float,
        drive_amplitude: float = 0.0,
        drive_seed: Optional[int] = None
    ):
        self.field = field
        self.gamma = gamma
        self.omega = omega
        self.epsilon = epsilon
        self.drive_amplitude = drive_amplitude

        # Generate random drive directions (fixed for reproducibility)
        rng = np.random.default_rng(drive_seed)
        drive_phases = rng.uniform(0, 2 * np.pi, field.manifold.N)
        self._drive = drive_amplitude * np.exp(1j * drive_phases)

        # Track total evolution time
        self.tau = 0.0

    def _compute_derivative(self) -> np.ndarray:
        """
        Compute ∂ψ/∂τ = -γψ + iωψ + D

        Returns
        -------
        dpsi_dtau : ndarray[complex]
            Time derivative of ψ
        """
        psi = self.field.psi
        dpsi_dtau = -self.gamma * psi + 1j * self.omega * psi + self._drive
        return dpsi_dtau

    def _enforce_floor(self) -> int:
        """
        Enforce floor constraint: |ψ| ≥ ε

        Radially projects any ψ with |ψ| < ε to |ψ| = ε.

        Returns
        -------
        floor_hits : int
            Number of nodes that hit floor
        """
        psi = self.field.psi
        amplitudes = np.abs(psi)

        # Find nodes below floor
        below_floor = amplitudes < self.epsilon
        n_hits = np.sum(below_floor)

        if n_hits > 0:
            # Radial projection: ψ → ε * (ψ / |ψ|)
            # Handle zero case (shouldn't happen, but be safe)
            phases = np.angle(psi[below_floor])
            psi[below_floor] = self.epsilon * np.exp(1j * phases)

            # Update field
            self.field.psi = psi

        return int(n_hits)

    def _compute_energy(self, dpsi_dtau: np.ndarray) -> float:
        """
        Compute energy from striving: E = ⟨|∂ψ/∂τ|²⟩

        Parameters
        ----------
        dpsi_dtau : ndarray[complex]
            Time derivative of ψ

        Returns
        -------
        energy : float
            Mean energy density
        """
        return np.mean(np.abs(dpsi_dtau) ** 2)

    def evolve_step(self, dt: float) -> dict:
        """
        Single evolution step using forward Euler.

        Steps:
        1. Compute dψ/dτ
        2. Update ψ(τ + dt) = ψ(τ) + dt·dψ/dτ
        3. Enforce floor constraint
        4. Compute diagnostics

        Parameters
        ----------
        dt : float
            Timestep size

        Returns
        -------
        diagnostics : dict
            - floor_hits: number of nodes hitting floor
            - global_cancel: global cancellation measure
            - mean_amp: mean amplitude
            - energy: energy density from striving
            - tau: current time
        """
        # Compute derivative
        dpsi_dtau = self._compute_derivative()

        # Forward Euler step
        self.field.psi = self.field.psi + dt * dpsi_dtau

        # Enforce floor
        floor_hits = self._enforce_floor()

        # Update time
        self.tau += dt

        # Compute diagnostics
        diagnostics = {
            'floor_hits': floor_hits,
            'global_cancel': self.field.global_cancellation_measure(),
            'mean_amp': self.field.mean_amplitude(),
            'energy': self._compute_energy(dpsi_dtau),
            'tau': self.tau
        }

        return diagnostics

    def evolve_trajectory(
        self,
        n_steps: int,
        dt: float,
        save_every: int = 1
    ) -> pd.DataFrame:
        """
        Evolve for multiple steps and save diagnostics.

        Parameters
        ----------
        n_steps : int
            Number of steps to evolve
        dt : float
            Timestep size
        save_every : int, optional
            Save diagnostics every N steps (default 1)

        Returns
        -------
        trajectory : DataFrame
            Columns: step, tau, floor_hits, global_cancel, mean_amp, energy
        """
        records = []

        for step in range(n_steps):
            # Evolve one step
            diag = self.evolve_step(dt)

            # Save diagnostics if requested
            if step % save_every == 0:
                record = {
                    'step': step,
                    'tau': diag['tau'],
                    'floor_hits': diag['floor_hits'],
                    'global_cancel': diag['global_cancel'],
                    'mean_amp': diag['mean_amp'],
                    'energy': diag['energy']
                }
                records.append(record)

        return pd.DataFrame(records)

    def reset(self) -> None:
        """Reset evolution time to zero."""
        self.tau = 0.0

"""
Emergent drive from floor constraint.

The anti-cancellation drive D emerges from the floor constraint itself:
- Floor constraint: C = |∫ψ| - ε ≥ 0
- Lagrange multiplier: λ enforces C ≥ 0
- Drive: D = λ · direction (points toward increasing |∫ψ|)

"The impossibility itself is the energy source." — Vision
"""

from typing import Dict, Any, Tuple
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField


class EmergentDrive:
    """
    Compute anti-cancellation drive from floor constraint.

    The floor (impossibility of ψ → 0) generates the drive (resistance).
    Self-bootstrapping: constraint → drive → striving → sustained constraint.

    Parameters
    ----------
    manifold : PreGeometricManifold
        Manifold topology
    epsilon : float
        Floor constraint value
    """

    def __init__(self, manifold: PreGeometricManifold, epsilon: float):
        self.manifold = manifold
        self.epsilon = epsilon

    def evaluate_constraint(self, psi: np.ndarray) -> float:
        """
        Evaluate floor constraint: C = |∫ψ| - ε

        C > 0: constraint satisfied (safe)
        C ≈ 0: approaching violation (critical)
        C < 0: violation (should not occur)

        Parameters
        ----------
        psi : ndarray[complex]
            Current field

        Returns
        -------
        constraint_value : float
            C = |∫ψ| - ε
        """
        # Discrete integral: ∫ψ dμ = (1/N) Σ ψ_i
        integral = np.mean(psi)
        global_amplitude = np.abs(integral)

        constraint = global_amplitude - self.epsilon

        return constraint

    def compute_multiplier(
        self,
        psi: np.ndarray,
        control_gain: float = 1.0,
        regularization: float = 0.001
    ) -> float:
        """
        Compute Lagrange multiplier λ(τ) from constraint proximity.

        Feedback control: λ = K / (C + δ)
        - C → 0: λ increases (strong drive needed)
        - C >> 0: λ decreases (weak drive sufficient)

        Parameters
        ----------
        psi : ndarray[complex]
            Current field
        control_gain : float
            Feedback gain K
        regularization : float
            Small δ to prevent λ → ∞

        Returns
        -------
        lambda_value : float
            Lagrange multiplier (≥ 0)
        """
        constraint = self.evaluate_constraint(psi)

        # Proportional control
        lambda_value = control_gain / (constraint + regularization)

        # Ensure non-negative
        lambda_value = max(0.0, lambda_value)

        return lambda_value

    def compute_drive(
        self,
        psi: np.ndarray,
        control_gain: float = 1.0,
        regularization: float = 0.001
    ) -> np.ndarray:
        """
        Compute emergent drive: D = λ · direction

        Direction points toward increasing |∫ψ|:
        For global constraint: D_i = λ · (∫ψ / |∫ψ|)

        Parameters
        ----------
        psi : ndarray[complex]
            Current field
        control_gain : float
            Control gain
        regularization : float
            Regularization parameter

        Returns
        -------
        drive : ndarray[complex]
            Emergent anti-cancellation drive at each node
        """
        N = len(psi)

        # Compute multiplier
        lambda_value = self.compute_multiplier(psi, control_gain, regularization)

        # Compute direction (gradient of constraint)
        # ∇C = ∇|∫ψ| = (∫ψ / |∫ψ|) * (1/N) for each node
        integral = np.mean(psi)
        global_amplitude = np.abs(integral)

        if global_amplitude < 1e-12:
            # Degenerate case: nearly zero, pick arbitrary direction
            direction = np.ones(N, dtype=complex) / N
        else:
            # Direction: uniform across nodes, aligned with global phase
            direction = integral / global_amplitude / N

        # Drive: λ · direction
        drive = lambda_value * direction * np.ones(N, dtype=complex)

        return drive

    def evolve_with_emergent_drive(
        self,
        field: FrustrationField,
        gamma: float,
        omega: float,
        n_steps: int,
        dt: float,
        control_gain: float = 1.0,
        regularization: float = 0.001
    ) -> Dict[str, Any]:
        """
        Evolve dynamics with emergent (not imposed) drive.

        Evolution: ∂ψ/∂τ = -γψ + iωψ + D_emergent(ψ, ε)

        Check: does system sustain itself without external input?

        Parameters
        ----------
        field : FrustrationField
            Field to evolve
        gamma, omega : float
            Dynamics parameters
        n_steps : int
            Number of evolution steps
        dt : float
            Timestep
        control_gain : float
            Drive control gain
        regularization : float
            Regularization parameter

        Returns
        -------
        diagnostics : dict
            - psi_history: field trajectory
            - floor_violations: count of |ψ_i| < ε
            - drive_amplitude_history: |D| over time
            - constraint_history: C(τ) over time
            - lambda_history: λ(τ) over time
            - energy_history: E(τ) over time
            - is_self_sustaining: bool (no collapse)
        """
        psi_history = [field.psi.copy()]
        drive_amplitude_history = []
        constraint_history = []
        lambda_history = []
        energy_history = []
        floor_violations_history = []

        for step in range(n_steps):
            psi = field.psi

            # Compute emergent drive
            drive = self.compute_drive(psi, control_gain, regularization)
            lambda_value = self.compute_multiplier(psi, control_gain, regularization)

            # Compute time derivative: ∂ψ/∂τ = -γψ + iωψ + D
            dpsi_dtau = -gamma * psi + 1j * omega * psi + drive

            # Forward Euler step
            psi_new = psi + dt * dpsi_dtau

            # Enforce floor (radial projection)
            amplitudes = np.abs(psi_new)
            below_floor = amplitudes < self.epsilon
            psi_new[below_floor] = self.epsilon * (psi_new[below_floor] / (amplitudes[below_floor] + 1e-12))

            # Update field
            field.psi = psi_new

            # Record diagnostics
            psi_history.append(psi_new.copy())
            drive_amplitude_history.append(np.mean(np.abs(drive)))
            constraint_history.append(self.evaluate_constraint(psi_new))
            lambda_history.append(lambda_value)
            energy_history.append(np.mean(np.abs(dpsi_dtau) ** 2))
            floor_violations_history.append(np.sum(below_floor))

        # Check if self-sustaining
        final_constraint = constraint_history[-1]
        mean_violations = np.mean(floor_violations_history)
        total_violations = np.sum(floor_violations_history)

        is_self_sustaining = (
            final_constraint > 0 and
            total_violations < n_steps * len(psi) * 0.05  # Less than 5% violation rate
        )

        diagnostics = {
            'psi_history': psi_history,
            'floor_violations': total_violations,
            'drive_amplitude_history': np.array(drive_amplitude_history),
            'constraint_history': np.array(constraint_history),
            'lambda_history': np.array(lambda_history),
            'energy_history': np.array(energy_history),
            'is_self_sustaining': is_self_sustaining,
            'final_constraint': final_constraint,
            'mean_violations_per_step': mean_violations
        }

        return diagnostics

    def compare_with_imposed_drive(
        self,
        field_emergent: FrustrationField,
        field_imposed: FrustrationField,
        imposed_amplitude: float,
        imposed_seed: int,
        gamma: float,
        omega: float,
        n_steps: int,
        dt: float,
        control_gain: float = 1.0,
        regularization: float = 0.001
    ) -> Dict[str, Any]:
        """
        Compare emergent drive with imposed drive (Phase 1).

        Run two parallel evolutions:
        1. With emergent drive D_emergent(ψ,ε)
        2. With imposed drive D_imposed (fixed amplitude)

        Parameters
        ----------
        field_emergent : FrustrationField
            Field for emergent evolution
        field_imposed : FrustrationField
            Field for imposed evolution (same initial state)
        imposed_amplitude : float
            Amplitude of imposed drive
        imposed_seed : int
            Random seed for imposed drive directions
        gamma, omega : float
            Dynamics parameters
        n_steps, dt : int, float
            Evolution parameters
        control_gain : float
            Emergent drive gain
        regularization : float
            Regularization parameter

        Returns
        -------
        comparison : dict
            Comparison metrics between emergent and imposed
        """
        # Evolve with emergent drive
        diag_emergent = self.evolve_with_emergent_drive(
            field_emergent, gamma, omega, n_steps, dt, control_gain, regularization
        )

        # Evolve with imposed drive
        rng = np.random.default_rng(imposed_seed)
        N = field_imposed.manifold.N
        imposed_phases = rng.uniform(0, 2 * np.pi, N)
        imposed_drive = imposed_amplitude * np.exp(1j * imposed_phases)

        energy_imposed = []
        floor_violations_imposed = []

        for step in range(n_steps):
            psi = field_imposed.psi

            # Time derivative with imposed drive
            dpsi_dtau = -gamma * psi + 1j * omega * psi + imposed_drive

            # Forward Euler
            psi_new = psi + dt * dpsi_dtau

            # Floor enforcement
            amplitudes = np.abs(psi_new)
            below_floor = amplitudes < self.epsilon
            psi_new[below_floor] = self.epsilon * (psi_new[below_floor] / (amplitudes[below_floor] + 1e-12))

            field_imposed.psi = psi_new

            energy_imposed.append(np.mean(np.abs(dpsi_dtau) ** 2))
            floor_violations_imposed.append(np.sum(below_floor))

        # Compute comparison metrics
        emergent_mean_energy = np.mean(diag_emergent['energy_history'])
        imposed_mean_energy = np.mean(energy_imposed)

        emergent_mean_drive = np.mean(diag_emergent['drive_amplitude_history'])
        imposed_mean_drive = imposed_amplitude

        energy_ratio = emergent_mean_energy / imposed_mean_energy if imposed_mean_energy > 0 else np.inf
        drive_ratio = emergent_mean_drive / imposed_mean_drive if imposed_mean_drive > 0 else np.inf

        are_comparable = (0.5 <= energy_ratio <= 2.0) and (0.5 <= drive_ratio <= 2.0)

        comparison = {
            'emergent_trajectory': diag_emergent,
            'imposed_mean_energy': imposed_mean_energy,
            'imposed_floor_violations': np.sum(floor_violations_imposed),
            'emergent_mean_energy': emergent_mean_energy,
            'emergent_mean_drive': emergent_mean_drive,
            'imposed_mean_drive': imposed_mean_drive,
            'energy_ratio': energy_ratio,
            'drive_ratio': drive_ratio,
            'are_comparable': are_comparable
        }

        return comparison

    def __repr__(self):
        return f"EmergentDrive(N={self.manifold.N}, ε={self.epsilon})"

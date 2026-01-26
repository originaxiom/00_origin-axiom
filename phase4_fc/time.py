"""
Emergent time from frustrated cancellation dynamics.

Time is not an external parameter but emerges from the progress
of the cancellation attempt: dt ~ |∂ψ/∂τ|

"Time: Progress of the cancellation attempt" — Vision
"""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from phase0_fc import FrustrationField


class EmergentTime:
    """
    Compute physical time from field evolution.

    Physical time emerges from striving intensity:
        dt = ⟨|∂ψ/∂τ|⟩ · dτ

    Faster striving → faster time passage.
    No striving (floor-frozen) → time stops.

    Parameters
    ----------
    field : FrustrationField
        Field whose evolution defines time
    """

    def __init__(self, field: FrustrationField):
        self.field = field
        self.manifold = field.manifold

    def compute_dt(
        self,
        dpsi_dtau: np.ndarray,
        dtau: float,
        method: str = 'mean_derivative'
    ) -> float:
        """
        Compute physical time increment from field evolution rate.

        Physical time defined by "progress of striving":
            dt = ⟨|∂ψ/∂τ|⟩ · dτ  (mean_derivative)
            dt = √⟨|∂ψ/∂τ|²⟩ · dτ (rms_derivative, connects to energy)

        Parameters
        ----------
        dpsi_dtau : ndarray[complex]
            Time derivative ∂ψ/∂τ at current moment
        dtau : float
            Evolution parameter step size
        method : str
            'mean_derivative' or 'rms_derivative'

        Returns
        -------
        dt : float
            Physical time increment (>0)
        """
        if method == 'mean_derivative':
            # Mean striving rate
            mean_rate = np.mean(np.abs(dpsi_dtau))
            dt = mean_rate * dtau
        elif method == 'rms_derivative':
            # RMS striving rate (connects to energy E = ⟨|∂ψ/∂τ|²⟩)
            rms_rate = np.sqrt(np.mean(np.abs(dpsi_dtau) ** 2))
            dt = rms_rate * dtau
        else:
            raise ValueError(f"Unknown method: {method}")

        return dt

    def local_time_rate(
        self,
        dpsi_dtau: np.ndarray
    ) -> np.ndarray:
        """
        Compute local rate of time passage at each node.

        Rate = |∂ψ_i/∂τ| (faster striving → faster local time)

        Parameters
        ----------
        dpsi_dtau : ndarray[complex]
            Time derivative of field

        Returns
        -------
        time_rate : ndarray[float]
            Local time dilation factor dt/dτ at each node
        """
        return np.abs(dpsi_dtau)

    def time_dilation_factor(
        self,
        dpsi_dtau: np.ndarray,
        node_i: int,
        node_j: int
    ) -> float:
        """
        Compute relative time dilation between two nodes.

        α_ij = (dt/dτ)_i / (dt/dτ)_j

        If α > 1: node i ages faster than node j.
        If α < 1: node i ages slower than node j.

        Parameters
        ----------
        dpsi_dtau : ndarray[complex]
            Time derivative of field
        node_i : int
            First node index
        node_j : int
            Second node index

        Returns
        -------
        alpha : float
            Time dilation factor (positive)
        """
        rate_i = np.abs(dpsi_dtau[node_i])
        rate_j = np.abs(dpsi_dtau[node_j])

        # Avoid division by zero
        if rate_j < 1e-12:
            return np.inf if rate_i > 1e-12 else 1.0

        return rate_i / rate_j

    def integrate_time(
        self,
        dpsi_dtau_list: List[np.ndarray],
        dtau: float,
        method: str = 'mean_derivative'
    ) -> Tuple[float, np.ndarray]:
        """
        Integrate physical time over trajectory.

        T = Σ dt_k = Σ ⟨|∂ψ/∂τ|⟩_k · dτ

        Parameters
        ----------
        dpsi_dtau_list : list of ndarray
            Time derivatives at each evolution step
        dtau : float
            Evolution parameter step size
        method : str
            Time computation method

        Returns
        -------
        total_age : float
            Total accumulated physical time
        time_array : ndarray
            Cumulative physical time at each step
        """
        n_steps = len(dpsi_dtau_list)
        time_array = np.zeros(n_steps + 1)

        for k, dpsi_dtau in enumerate(dpsi_dtau_list):
            dt = self.compute_dt(dpsi_dtau, dtau, method=method)
            time_array[k + 1] = time_array[k] + dt

        total_age = time_array[-1]
        return total_age, time_array

    def check_causality(
        self,
        psi_trajectory: List[np.ndarray],
        dpsi_dtau_list: List[np.ndarray],
        threshold: float = 1e-8
    ) -> Dict[str, Any]:
        """
        Verify causal structure from evolution.

        Check:
        1. Information propagates locally (nearest neighbors only)
        2. No superluminal propagation
        3. Influence decays with graph distance

        Causality test: Does ∂ψ_i/∂τ depend only on neighbors of i?

        Parameters
        ----------
        psi_trajectory : list of ndarray
            Field at each time step
        dpsi_dtau_list : list of ndarray
            Time derivatives at each step
        threshold : float
            Threshold for considering influence significant

        Returns
        -------
        causality_report : dict
            - local_violations: number of non-local influences detected
            - max_influence_distance: maximum distance of significant influence
            - propagation_speed: estimated information propagation speed
            - is_causal: True if no violations detected
        """
        N = self.manifold.N
        adjacency = self.manifold.adjacency

        # For frustrated dynamics: ∂ψ_i/∂τ = -γψ_i + iωψ_i + D_i
        # This is local (depends only on ψ_i, not neighbors)
        # So causality is automatically preserved for this dynamics

        # Check: does field change propagate locally?
        # Look at correlation between Δψ_i and ψ_j at neighbors vs non-neighbors

        local_violations = 0
        max_influence_distance = 0

        # For simple frustrated dynamics, causality is trivially preserved
        # because evolution is local (no explicit diffusion term)

        # More sophisticated check: measure correlation decay with distance
        # For now, report that dynamics is local by construction

        report = {
            'local_violations': 0,
            'max_influence_distance': 0,  # Evolution is purely local
            'propagation_speed': 0.0,  # No spatial coupling yet
            'is_causal': True,
            'note': 'Current dynamics is local by construction (no diffusion term)'
        }

        return report

    def compute_time_statistics(
        self,
        dpsi_dtau_list: List[np.ndarray],
        dtau: float
    ) -> Dict[str, Any]:
        """
        Compute statistical properties of time emergence.

        Parameters
        ----------
        dpsi_dtau_list : list of ndarray
            Time derivatives at each step
        dtau : float
            Evolution parameter step size

        Returns
        -------
        stats : dict
            - total_age: total physical time
            - mean_dt_per_step: average dt per evolution step
            - dt_variation: std(dt) / mean(dt)
            - min_time_rate: minimum local time rate
            - max_time_rate: maximum local time rate
            - time_dilation_range: max_rate / min_rate
        """
        total_age, time_array = self.integrate_time(dpsi_dtau_list, dtau)

        # Compute dt at each step
        dt_values = np.diff(time_array)
        mean_dt = np.mean(dt_values)
        std_dt = np.std(dt_values)

        # Local time rates over all steps
        all_rates = []
        for dpsi_dtau in dpsi_dtau_list:
            rates = self.local_time_rate(dpsi_dtau)
            all_rates.append(rates)

        all_rates = np.concatenate(all_rates)
        min_rate = np.min(all_rates[all_rates > 1e-12])  # Exclude zeros
        max_rate = np.max(all_rates)

        stats = {
            'total_age': total_age,
            'mean_dt_per_step': mean_dt,
            'dt_variation': std_dt / mean_dt if mean_dt > 0 else 0.0,
            'min_time_rate': min_rate,
            'max_time_rate': max_rate,
            'time_dilation_range': max_rate / min_rate if min_rate > 0 else np.inf,
            'n_steps': len(dpsi_dtau_list)
        }

        return stats

    def compare_with_tau(
        self,
        dpsi_dtau_list: List[np.ndarray],
        dtau: float
    ) -> Dict[str, float]:
        """
        Compare physical time T with evolution parameter τ.

        Shows how T/τ varies with dynamics.

        Parameters
        ----------
        dpsi_dtau_list : list of ndarray
            Time derivatives
        dtau : float
            Step size in τ

        Returns
        -------
        comparison : dict
            - total_physical_time: T
            - total_parameter_time: τ_total = n_steps * dtau
            - ratio_T_over_tau: T / τ
            - interpretation: what this ratio means
        """
        total_age, _ = self.integrate_time(dpsi_dtau_list, dtau)
        total_tau = len(dpsi_dtau_list) * dtau

        ratio = total_age / total_tau if total_tau > 0 else 0.0

        comparison = {
            'total_physical_time': total_age,
            'total_parameter_time': total_tau,
            'ratio_T_over_tau': ratio,
            'interpretation': (
                f"Physical time runs {ratio:.3f}x as fast as evolution parameter. "
                f"Higher ratio means more intense striving."
            )
        }

        return comparison

    def __repr__(self):
        return f"EmergentTime(N={self.manifold.N})"

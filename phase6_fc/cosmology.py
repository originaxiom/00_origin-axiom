"""
Phase 6_FC: Cosmological Observables

Extract cosmological observables (H, a, w, ρ) from frustrated cancellation dynamics
to test whether the framework describes the actual universe.

Energy from striving: ρ = ⟨|∂ψ/∂τ|²⟩
Hubble from expansion: H = (1/a)(da/dt)
Equation of state: w = P/ρ
Scale factor: a from field structure

Classes
-------
CosmologicalObservables
    Extract and track cosmological observables from frustrated dynamics
"""

import numpy as np
from typing import Dict, Optional, Tuple
from phase0_fc.manifold import PreGeometricManifold
from phase0_fc.field import FrustrationField
from phase1_fc.dynamics import FrustratedDynamics
from phase4_fc.time import EmergentTime


class CosmologicalObservables:
    """
    Extract cosmological observables from frustrated cancellation dynamics.

    Maps frustrated striving → cosmological evolution
    - Energy density: ρ(τ) = ⟨|∂ψ/∂τ|²⟩
    - Hubble parameter: H(τ) = (1/a)(da/dt)
    - Scale factor: a(τ) from field evolution
    - Equation of state: w = P/ρ

    Parameters
    ----------
    manifold : PreGeometricManifold
        Topology structure
    dynamics : FrustratedDynamics
        Evolution equations
    time : EmergentTime
        Physical time computation
    """

    def __init__(self,
                 manifold: PreGeometricManifold,
                 dynamics: FrustratedDynamics,
                 time: EmergentTime):
        self.manifold = manifold
        self.dynamics = dynamics
        self.time = time
        self.N = manifold.N

    def compute_energy_density(self,
                               psi: np.ndarray,
                               psi_dot: np.ndarray) -> float:
        """
        Compute spatial-average energy density from striving.

        ρ(τ) = ⟨|∂ψ/∂τ|²⟩

        Energy emerges from the rate of cancellation attempt.
        Spatial average over manifold.

        Parameters
        ----------
        psi : np.ndarray, shape (N,)
            Current field state
        psi_dot : np.ndarray, shape (N,)
            Field time derivative ∂ψ/∂τ

        Returns
        -------
        rho : float
            Energy density (spatial average)
        """
        # Energy from striving: |∂ψ/∂τ|²
        local_energy = np.abs(psi_dot) ** 2

        # Spatial average
        rho = np.mean(local_energy)

        return float(rho)

    def compute_pressure(self,
                        psi: np.ndarray,
                        psi_dot: np.ndarray,
                        method: str = 'isotropic') -> float:
        """
        Compute pressure from field dynamics.

        For isotropic case: P = (1/3)⟨|∂ψ/∂τ|²⟩
        (Standard relativistic fluid relation for radiation-like)

        Parameters
        ----------
        psi : np.ndarray
            Current field state
        psi_dot : np.ndarray
            Field derivative
        method : str
            'isotropic': P = ρ/3
            'trace': P from stress tensor trace

        Returns
        -------
        P : float
            Pressure
        """
        rho = self.compute_energy_density(psi, psi_dot)

        if method == 'isotropic':
            # Isotropic approximation: P = ρ/3
            # (This assumes relativistic, pressure-like behavior)
            P = rho / 3.0
        elif method == 'trace':
            # From stress tensor trace
            # For scalar field: P ≈ (kinetic - potential)
            # Here: P ≈ ρ - 2V where V ~ floor constraint energy
            # Simplified: P ≈ 0 (matter-like) for now
            P = 0.0
        else:
            raise ValueError(f"Unknown pressure method: {method}")

        return float(P)

    def compute_equation_of_state(self,
                                  rho: float,
                                  pressure: float) -> float:
        """
        Compute equation of state parameter w = P/ρ.

        w = -1: cosmological constant (Λ)
        w = 0: matter
        w = 1/3: radiation
        w < -1: phantom energy

        Parameters
        ----------
        rho : float
            Energy density
        pressure : float
            Pressure

        Returns
        -------
        w : float
            Equation of state parameter
        """
        if rho < 1e-12:
            # Avoid division by zero for empty space
            return 0.0

        w = pressure / rho
        return float(w)

    def compute_scale_factor(self,
                            psi: np.ndarray,
                            method: str = 'amplitude',
                            normalize_to: Optional[float] = None) -> float:
        """
        Compute scale factor from field state.

        Scale factor represents "size" of the universe.
        Multiple definitions possible:

        - 'amplitude': a ~ ⟨|ψ|⟩ (mean field amplitude)
        - 'correlation': a ~ correlation length (spatial structure size)
        - 'volume': a ~ effective volume from geometry

        Parameters
        ----------
        psi : np.ndarray
            Current field state
        method : str
            Method for scale factor definition
        normalize_to : float, optional
            Normalization value (typically a(τ=0) = 1)

        Returns
        -------
        a : float
            Scale factor (dimensionless)
        """
        if method == 'amplitude':
            # Scale factor from mean amplitude
            a = np.mean(np.abs(psi))

        elif method == 'correlation':
            # Scale factor from correlation length
            # Compute spatial correlations
            correlations = []
            for i in range(min(10, self.N)):  # Sample subset
                for j in self.manifold.adjacency[i]:
                    corr = np.abs(np.dot(psi[i].conj(), psi[j]))
                    correlations.append(corr)

            if len(correlations) > 0:
                a = np.mean(correlations)
            else:
                a = 1.0

        elif method == 'volume':
            # Scale factor from "effective volume"
            # Volume ~ sum of |ψ|² (occupation)
            volume = np.sum(np.abs(psi) ** 2)
            a = (volume / self.N) ** (1/3)  # Cube root for 3D

        else:
            raise ValueError(f"Unknown scale factor method: {method}")

        # Normalize if requested
        if normalize_to is not None:
            a = a / normalize_to

        return float(a)

    def compute_hubble_parameter(self,
                                 a: float,
                                 a_prev: float,
                                 dt: float) -> float:
        """
        Compute Hubble parameter H = (1/a)(da/dt).

        Uses finite difference for da/dt.

        Parameters
        ----------
        a : float
            Current scale factor
        a_prev : float
            Previous scale factor
        dt : float
            Time step (physical time)

        Returns
        -------
        H : float
            Hubble parameter
        """
        if dt < 1e-12 or a < 1e-12:
            return 0.0

        # da/dt from finite difference
        da_dt = (a - a_prev) / dt

        # H = (1/a)(da/dt)
        H = da_dt / a

        return float(H)

    def compute_hubble_from_friedmann(self,
                                      rho: float,
                                      k: float = 0.0) -> float:
        """
        Compute Hubble parameter from Friedmann equation.

        H² = (8πG/3)ρ - k/a²

        Simplified (units where 8πG/3 = 1, k = 0):
        H² ≈ ρ → H ≈ √ρ

        Parameters
        ----------
        rho : float
            Energy density
        k : float
            Spatial curvature (0 = flat)

        Returns
        -------
        H : float
            Hubble parameter from Friedmann
        """
        if rho < 0:
            return 0.0

        # Simplified Friedmann: H² ≈ ρ (in natural units)
        H = np.sqrt(rho)

        return float(H)

    def compute_acceleration(self,
                            a: float,
                            a_prev: float,
                            a_prev2: float,
                            dt: float) -> float:
        """
        Compute acceleration d²a/dt² from finite differences.

        Positive → accelerating expansion
        Negative → decelerating expansion

        Parameters
        ----------
        a : float
            Current scale factor
        a_prev : float
            Previous scale factor
        a_prev2 : float
            Scale factor two steps back
        dt : float
            Time step

        Returns
        -------
        a_ddot : float
            Second derivative d²a/dt²
        """
        if dt < 1e-12:
            return 0.0

        # Central difference: d²a/dt² ≈ (a - 2·a_prev + a_prev2) / dt²
        a_ddot = (a - 2*a_prev + a_prev2) / (dt ** 2)

        return float(a_ddot)

    def compute_derivative(self,
                          psi: np.ndarray,
                          gamma: float,
                          omega: float,
                          drive: np.ndarray) -> np.ndarray:
        """
        Compute field derivative ∂ψ/∂τ = -γψ + iωψ + D.

        Parameters
        ----------
        psi : np.ndarray
            Current field state
        gamma : float
            Damping parameter
        omega : float
            Rotation parameter
        drive : np.ndarray
            Drive field

        Returns
        -------
        psi_dot : np.ndarray
            Field derivative
        """
        psi_dot = -gamma * psi + 1j * omega * psi + drive
        return psi_dot

    def evolve_cosmology(self,
                        field: FrustrationField,
                        gamma: float,
                        omega: float,
                        epsilon: float,
                        n_steps: int,
                        dtau: float,
                        use_emergent_drive: bool = True,
                        control_gain: float = 1.0,
                        scale_method: str = 'amplitude',
                        pressure_method: str = 'isotropic') -> Dict[str, np.ndarray]:
        """
        Evolve system and track cosmological observables.

        Runs frustrated dynamics while extracting H(τ), a(τ), w(τ), ρ(τ).

        Parameters
        ----------
        field : FrustrationField
            Initial field state
        gamma : float
            Damping parameter
        omega : float
            Rotation parameter
        epsilon : float
            Floor constraint value
        n_steps : int
            Number of evolution steps
        dtau : float
            Parameter time step
        use_emergent_drive : bool
            If True, use Phase 5 emergent drive
            If False, use imposed drive (Phase 1)
        control_gain : float
            Drive control gain (if emergent)
        scale_method : str
            Method for scale factor computation
        pressure_method : str
            Method for pressure computation

        Returns
        -------
        diagnostics : dict
            'tau': parameter time array (n_steps+1,)
            'physical_time': emergent time array (n_steps+1,)
            'rho': energy density history (n_steps+1,)
            'pressure': pressure history (n_steps+1,)
            'H_kinematic': Hubble from da/dt (n_steps+1,)
            'H_friedmann': Hubble from Friedmann (n_steps+1,)
            'a': scale factor history (n_steps+1,)
            'w': equation of state history (n_steps+1,)
            'a_ddot': acceleration history (n_steps+1,)
            'psi_final': final field state
        """
        # Initialize storage
        tau_history = np.zeros(n_steps + 1)
        t_history = np.zeros(n_steps + 1)
        rho_history = np.zeros(n_steps + 1)
        pressure_history = np.zeros(n_steps + 1)
        H_kinematic_history = np.zeros(n_steps + 1)
        H_friedmann_history = np.zeros(n_steps + 1)
        a_history = np.zeros(n_steps + 1)
        w_history = np.zeros(n_steps + 1)
        a_ddot_history = np.zeros(n_steps + 1)

        # Current state
        psi = field.psi.copy()
        tau = 0.0
        t_physical = 0.0

        # Compute initial scale factor (for normalization)
        a_initial = self.compute_scale_factor(psi, method=scale_method)

        # Initial drive (imposed, uniform)
        initial_drive = np.ones(self.N, dtype=complex) * 0.05

        # Initial observables
        psi_dot = self.compute_derivative(psi, gamma, omega, initial_drive)
        rho = self.compute_energy_density(psi, psi_dot)
        pressure = self.compute_pressure(psi, psi_dot, method=pressure_method)
        a = self.compute_scale_factor(psi, method=scale_method,
                                      normalize_to=a_initial)
        w = self.compute_equation_of_state(rho, pressure)
        H_f = self.compute_hubble_from_friedmann(rho)

        # Store initial values
        tau_history[0] = tau
        t_history[0] = t_physical
        rho_history[0] = rho
        pressure_history[0] = pressure
        H_kinematic_history[0] = 0.0  # No previous step
        H_friedmann_history[0] = H_f
        a_history[0] = a
        w_history[0] = w
        a_ddot_history[0] = 0.0

        # Previous values for derivatives
        a_prev = a
        a_prev2 = a

        # Evolution loop
        for step in range(n_steps):
            # Compute drive
            if use_emergent_drive:
                # Use Phase 5 emergent drive
                from phase5_fc.drive import EmergentDrive
                drive_computer = EmergentDrive(self.manifold, epsilon)
                drive = drive_computer.compute_drive(psi, control_gain=control_gain)
            else:
                # Use imposed drive (uniform)
                drive = np.ones(self.N, dtype=complex) * 0.05

            # Compute derivative
            psi_dot = self.compute_derivative(psi, gamma, omega, drive)

            # Forward Euler step
            psi_new = psi + psi_dot * dtau

            # Enforce floor: |ψ| ≥ ε
            amplitudes = np.abs(psi_new)
            floor_violations = amplitudes < epsilon
            if np.any(floor_violations):
                # Radial projection to floor
                psi_new[floor_violations] = (epsilon / amplitudes[floor_violations]) * psi_new[floor_violations]

            # Update time
            tau += dtau
            dt_physical = self.time.compute_dt(psi_dot, dtau, method='mean_derivative')
            t_physical += dt_physical

            # Compute observables
            rho = self.compute_energy_density(psi_new, psi_dot)
            pressure = self.compute_pressure(psi_new, psi_dot, method=pressure_method)
            a_new = self.compute_scale_factor(psi_new, method=scale_method,
                                             normalize_to=a_initial)
            w = self.compute_equation_of_state(rho, pressure)

            # Hubble parameters
            H_k = self.compute_hubble_parameter(a_new, a_prev, dt_physical)
            H_f = self.compute_hubble_from_friedmann(rho)

            # Acceleration
            a_ddot = self.compute_acceleration(a_new, a_prev, a_prev2, dt_physical)

            # Store
            tau_history[step + 1] = tau
            t_history[step + 1] = t_physical
            rho_history[step + 1] = rho
            pressure_history[step + 1] = pressure
            H_kinematic_history[step + 1] = H_k
            H_friedmann_history[step + 1] = H_f
            a_history[step + 1] = a_new
            w_history[step + 1] = w
            a_ddot_history[step + 1] = a_ddot

            # Update for next step
            psi = psi_new
            a_prev2 = a_prev
            a_prev = a_new

        diagnostics = {
            'tau': tau_history,
            'physical_time': t_history,
            'rho': rho_history,
            'pressure': pressure_history,
            'H_kinematic': H_kinematic_history,
            'H_friedmann': H_friedmann_history,
            'a': a_history,
            'w': w_history,
            'a_ddot': a_ddot_history,
            'psi_final': psi
        }

        return diagnostics

    def __repr__(self) -> str:
        return (f"CosmologicalObservables(N={self.N}, "
                f"manifold={self.manifold.topology_type})")

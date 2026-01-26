"""
Unit tests for Phase 6_FC: Cosmological Observables

Tests individual methods of CosmologicalObservables class.
"""

import pytest
import numpy as np
from phase0_fc.manifold import PreGeometricManifold
from phase0_fc.field import FrustrationField
from phase1_fc.dynamics import FrustratedDynamics
from phase4_fc.time import EmergentTime
from phase6_fc.cosmology import CosmologicalObservables


class TestCosmologicalObservablesBasics:
    """Test initialization and basic functionality."""

    def test_initialization(self):
        """Test that CosmologicalObservables initializes correctly."""
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)

        cosmo = CosmologicalObservables(manifold, dynamics, time)

        assert cosmo.N == 50
        assert cosmo.manifold == manifold
        assert cosmo.dynamics == dynamics
        assert cosmo.time == time

    def test_repr(self):
        """Test string representation."""
        manifold = PreGeometricManifold(N_nodes=30, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)

        cosmo = CosmologicalObservables(manifold, dynamics, time)
        repr_str = repr(cosmo)

        assert 'CosmologicalObservables' in repr_str
        assert 'N=30' in repr_str
        assert 'cubic_3d' in repr_str


class TestEnergyDensity:
    """Test energy density computation."""

    def test_energy_density_positive(self):
        """Energy density should be positive for non-zero derivative."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        psi_dot = np.ones(40, dtype=complex) * 0.1  # Non-zero derivative

        rho = cosmo.compute_energy_density(psi, psi_dot)

        assert rho > 0
        assert np.isfinite(rho)

    def test_energy_density_zero_for_frozen(self):
        """Energy density should be zero for frozen field."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        psi_dot = np.zeros(40, dtype=complex)  # Frozen

        rho = cosmo.compute_energy_density(psi, psi_dot)

        assert rho == 0.0

    def test_energy_density_scales_with_amplitude(self):
        """Energy density should scale with |∂ψ/∂τ|²."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        psi_dot_1 = np.ones(40, dtype=complex) * 0.1
        psi_dot_2 = np.ones(40, dtype=complex) * 0.2  # 2x larger

        rho_1 = cosmo.compute_energy_density(psi, psi_dot_1)
        rho_2 = cosmo.compute_energy_density(psi, psi_dot_2)

        # Should scale quadratically
        assert rho_2 / rho_1 == pytest.approx(4.0, rel=1e-10)


class TestPressure:
    """Test pressure computation."""

    def test_pressure_isotropic(self):
        """Isotropic pressure should be P = ρ/3."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        psi_dot = np.ones(40, dtype=complex) * 0.1

        rho = cosmo.compute_energy_density(psi, psi_dot)
        P = cosmo.compute_pressure(psi, psi_dot, method='isotropic')

        assert P == pytest.approx(rho / 3.0, rel=1e-10)

    def test_pressure_trace(self):
        """Trace method should give matter-like (P ≈ 0)."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        psi_dot = np.ones(40, dtype=complex) * 0.1

        P = cosmo.compute_pressure(psi, psi_dot, method='trace')

        assert P == 0.0


class TestEquationOfState:
    """Test equation of state w = P/ρ."""

    def test_w_radiation_like(self):
        """For isotropic P = ρ/3, w should be 1/3."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        psi_dot = np.ones(40, dtype=complex) * 0.1

        rho = cosmo.compute_energy_density(psi, psi_dot)
        P = cosmo.compute_pressure(psi, psi_dot, method='isotropic')
        w = cosmo.compute_equation_of_state(rho, P)

        assert w == pytest.approx(1/3, rel=1e-10)

    def test_w_matter_like(self):
        """For P = 0, w should be 0."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        psi_dot = np.ones(40, dtype=complex) * 0.1

        rho = cosmo.compute_energy_density(psi, psi_dot)
        P = cosmo.compute_pressure(psi, psi_dot, method='trace')
        w = cosmo.compute_equation_of_state(rho, P)

        assert w == 0.0

    def test_w_zero_density(self):
        """For ρ = 0, w should default to 0."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        w = cosmo.compute_equation_of_state(rho=0.0, pressure=0.0)

        assert w == 0.0


class TestScaleFactor:
    """Test scale factor computation."""

    def test_scale_factor_amplitude(self):
        """Scale factor from amplitude should be positive."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        a = cosmo.compute_scale_factor(psi, method='amplitude')

        assert a > 0
        assert np.isfinite(a)

    def test_scale_factor_normalization(self):
        """Normalized scale factor should be 1."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        a_raw = cosmo.compute_scale_factor(psi, method='amplitude')
        a_norm = cosmo.compute_scale_factor(psi, method='amplitude',
                                           normalize_to=a_raw)

        assert a_norm == pytest.approx(1.0, rel=1e-10)

    def test_scale_factor_correlation(self):
        """Correlation method should give positive result."""
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        a = cosmo.compute_scale_factor(psi, method='correlation')

        assert a > 0
        assert np.isfinite(a)

    def test_scale_factor_volume(self):
        """Volume method should give positive result."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        psi = field.psi.copy()
        a = cosmo.compute_scale_factor(psi, method='volume')

        assert a > 0
        assert np.isfinite(a)


class TestHubbleParameter:
    """Test Hubble parameter computation."""

    def test_hubble_expansion(self):
        """H > 0 for expanding universe."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        a = 1.0
        a_prev = 0.9  # Expanding
        dt = 0.1

        H = cosmo.compute_hubble_parameter(a, a_prev, dt)

        assert H > 0  # Expansion

    def test_hubble_contraction(self):
        """H < 0 for contracting universe."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        a = 0.9
        a_prev = 1.0  # Contracting
        dt = 0.1

        H = cosmo.compute_hubble_parameter(a, a_prev, dt)

        assert H < 0  # Contraction

    def test_hubble_static(self):
        """H = 0 for static universe."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        a = 1.0
        a_prev = 1.0  # Static
        dt = 0.1

        H = cosmo.compute_hubble_parameter(a, a_prev, dt)

        assert H == 0.0

    def test_hubble_friedmann(self):
        """Friedmann relation H² ~ ρ."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        rho = 0.25  # → H = 0.5

        H = cosmo.compute_hubble_from_friedmann(rho)

        assert H == pytest.approx(0.5, rel=1e-10)

    def test_hubble_friedmann_zero_density(self):
        """H = 0 for ρ = 0."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        H = cosmo.compute_hubble_from_friedmann(rho=0.0)

        assert H == 0.0


class TestAcceleration:
    """Test acceleration computation."""

    def test_acceleration_accelerating(self):
        """d²a/dt² > 0 for accelerating expansion."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        # a increasing faster (accelerating)
        a = 1.21
        a_prev = 1.1
        a_prev2 = 1.0
        dt = 0.1

        a_ddot = cosmo.compute_acceleration(a, a_prev, a_prev2, dt)

        assert a_ddot > 0

    def test_acceleration_decelerating(self):
        """d²a/dt² < 0 for decelerating expansion."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        # a increasing slower
        a = 1.19
        a_prev = 1.1
        a_prev2 = 1.0
        dt = 0.1

        a_ddot = cosmo.compute_acceleration(a, a_prev, a_prev2, dt)

        assert a_ddot < 0

    def test_acceleration_constant_velocity(self):
        """d²a/dt² ≈ 0 for constant expansion rate."""
        manifold = PreGeometricManifold(N_nodes=40, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        # Linear expansion
        a = 1.2
        a_prev = 1.1
        a_prev2 = 1.0
        dt = 0.1

        a_ddot = cosmo.compute_acceleration(a, a_prev, a_prev2, dt)

        assert abs(a_ddot) < 1e-10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

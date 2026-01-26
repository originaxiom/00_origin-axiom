"""
Integration tests for Phase 6_FC: Cosmological Observables

Tests full pipeline from Phase 0 through Phase 6.
"""

import pytest
import numpy as np
from phase0_fc.manifold import PreGeometricManifold
from phase0_fc.field import FrustrationField
from phase1_fc.dynamics import FrustratedDynamics
from phase4_fc.time import EmergentTime
from phase6_fc.cosmology import CosmologicalObservables


class TestPhase6Integration:
    """Test full pipeline integration."""

    def test_full_pipeline(self):
        """Test complete Phase 0-6 pipeline."""
        # Phase 0: Pre-geometric setup
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        # Phase 1: Frustrated dynamics
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)

        # Phase 4: Emergent time
        time = EmergentTime(field)

        # Phase 6: Cosmological observables
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        # Evolve and extract observables
        diagnostics = cosmo.evolve_cosmology(
            field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            n_steps=20,
            dtau=0.01,
            use_emergent_drive=True,
            control_gain=1.0
        )

        # Verify all observables exist
        assert 'tau' in diagnostics
        assert 'physical_time' in diagnostics
        assert 'rho' in diagnostics
        assert 'H_kinematic' in diagnostics
        assert 'H_friedmann' in diagnostics
        assert 'a' in diagnostics
        assert 'w' in diagnostics
        assert 'psi_final' in diagnostics

        # Verify shapes
        assert diagnostics['tau'].shape == (21,)
        assert diagnostics['rho'].shape == (21,)
        assert diagnostics['a'].shape == (21,)

        # Verify no NaNs or infinities
        assert np.all(np.isfinite(diagnostics['rho']))
        assert np.all(np.isfinite(diagnostics['a']))
        assert np.all(np.isfinite(diagnostics['physical_time']))

    def test_energy_positivity(self):
        """Energy density should remain positive."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True
        )

        rho = diagnostics['rho']

        # All energy densities should be positive
        assert np.all(rho >= 0)
        assert np.all(rho < 1e6)  # Bounded

    def test_scale_factor_monotonic(self):
        """Scale factor should evolve monotonically (expand or contract)."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True
        )

        a = diagnostics['a']

        # Check monotonicity
        da = np.diff(a)

        # Either all positive (expansion) or all negative (contraction)
        # Allow some numerical noise
        expanding = np.sum(da > 0)
        contracting = np.sum(da < 0)

        # Should be predominantly one direction
        assert (expanding > 25 or contracting > 25)

    def test_time_monotonic(self):
        """Physical time should increase monotonically."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True
        )

        t = diagnostics['physical_time']

        # Time should increase
        dt = np.diff(t)
        assert np.all(dt >= 0)

    def test_hubble_consistency(self):
        """Hubble from kinematics should roughly match Friedmann."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=50, dtau=0.01,
            use_emergent_drive=True
        )

        H_k = diagnostics['H_kinematic'][1:]  # Skip first (no previous)
        H_f = diagnostics['H_friedmann'][1:]

        # Should be same order of magnitude
        # (May differ due to numerical derivatives vs. analytic)
        for i in range(len(H_k)):
            if abs(H_f[i]) > 1e-6:  # Non-zero
                ratio = H_k[i] / H_f[i] if abs(H_k[i]) > 1e-12 else 0.0
                # Allow wide tolerance (different definitions)
                assert 0.01 < abs(ratio) < 100 or abs(H_k[i]) < 1e-6

    def test_equation_of_state_physical(self):
        """Equation of state should be in physical range."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True,
            pressure_method='isotropic'
        )

        w = diagnostics['w']

        # w should be in physical range
        # Isotropic: w = 1/3
        assert np.all(w >= -2.0)  # No extreme phantom
        assert np.all(w <= 2.0)   # No extreme stiff matter


class TestComparison:
    """Test comparison with known cosmological models."""

    def test_imposed_vs_emergent_drive(self):
        """Compare evolution with imposed vs emergent drive."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field_imposed = FrustrationField(manifold, seed=42)
        field_imposed.initialize_random()
        field_emergent = FrustrationField(manifold, seed=43)
        field_emergent.initialize_random()
        dynamics = FrustratedDynamics(field_imposed, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field_imposed)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        # Evolution with imposed drive
        diag_imposed = cosmo.evolve_cosmology(
            field_imposed, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=False  # Imposed
        )

        # Evolution with emergent drive
        diag_emergent = cosmo.evolve_cosmology(
            field_emergent, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True   # Emergent
        )

        # Both should produce finite results
        assert np.all(np.isfinite(diag_imposed['rho']))
        assert np.all(np.isfinite(diag_emergent['rho']))

        # Energy densities should be comparable order of magnitude
        rho_imp_mean = np.mean(diag_imposed['rho'][10:])  # Skip transient
        rho_em_mean = np.mean(diag_emergent['rho'][10:])

        if rho_imp_mean > 1e-6 and rho_em_mean > 1e-6:
            ratio = rho_em_mean / rho_imp_mean
            # Should be within 2 orders of magnitude
            assert 0.01 < ratio < 100

    def test_reproducibility(self):
        """Results should be reproducible with fixed seed."""
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')

        # Run 1
        np.random.seed(12345)
        field1 = FrustrationField(manifold, seed=12345)
        field1.initialize_random()
        dynamics = FrustratedDynamics(field1, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field1)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diag1 = cosmo.evolve_cosmology(
            field1, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=20, dtau=0.01,
            use_emergent_drive=True
        )

        # Run 2 (same seed)
        np.random.seed(12345)
        field2 = FrustrationField(manifold, seed=12345)
        field2.initialize_random()
        diag2 = cosmo.evolve_cosmology(
            field2, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=20, dtau=0.01,
            use_emergent_drive=True
        )

        # Should match exactly
        np.testing.assert_allclose(diag1['rho'], diag2['rho'], rtol=1e-10)
        np.testing.assert_allclose(diag1['a'], diag2['a'], rtol=1e-10)


class TestScaleFactorMethods:
    """Test different scale factor computation methods."""

    def test_amplitude_method(self):
        """Test amplitude-based scale factor."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True,
            scale_method='amplitude'
        )

        a = diagnostics['a']

        # Should start at 1 (normalized)
        assert a[0] == pytest.approx(1.0, rel=1e-6)
        assert np.all(a > 0)
        assert np.all(np.isfinite(a))

    def test_correlation_method(self):
        """Test correlation-based scale factor."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True,
            scale_method='correlation'
        )

        a = diagnostics['a']

        # Should start at 1
        assert a[0] == pytest.approx(1.0, rel=1e-6)
        assert np.all(a > 0)
        assert np.all(np.isfinite(a))

    def test_volume_method(self):
        """Test volume-based scale factor."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True,
            scale_method='volume'
        )

        a = diagnostics['a']

        # Should start at 1
        assert a[0] == pytest.approx(1.0, rel=1e-6)
        assert np.all(a > 0)
        assert np.all(np.isfinite(a))


class TestPressureMethods:
    """Test different pressure computation methods."""

    def test_isotropic_pressure(self):
        """Test isotropic pressure (w = 1/3)."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True,
            pressure_method='isotropic'
        )

        w = diagnostics['w']

        # Should be approximately 1/3 (radiation-like)
        mean_w = np.mean(w[10:])  # Skip transient
        assert mean_w == pytest.approx(1/3, rel=0.05)

    def test_trace_pressure(self):
        """Test trace pressure (w = 0)."""
        np.random.seed(20260126)
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()
        dynamics = FrustratedDynamics(field, gamma=0.1, omega=1.0, epsilon=0.01)
        time = EmergentTime(field)
        cosmo = CosmologicalObservables(manifold, dynamics, time)

        diagnostics = cosmo.evolve_cosmology(
            field, gamma=0.1, omega=1.0, epsilon=0.01, n_steps=30, dtau=0.01,
            use_emergent_drive=True,
            pressure_method='trace'
        )

        w = diagnostics['w']

        # Should be 0 (matter-like)
        assert np.all(w == 0.0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

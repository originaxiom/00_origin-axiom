"""
Tests for emergent time computation.

Tests:
- Time increment computation
- Local time rates
- Time integration
- Monotonicity
- Reproducibility
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase4_fc import EmergentTime


class TestEmergentTime:
    """Test basic time computation functionality."""

    def test_initialization(self):
        """Test EmergentTime initialization."""
        manifold = PreGeometricManifold(N_nodes=10, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        assert time_tracker.field is field
        assert time_tracker.manifold is manifold

    def test_compute_dt_mean_derivative(self):
        """Test dt computation with mean derivative method."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Create mock derivative
        dpsi_dtau = np.ones(8, dtype=complex) * 0.5
        dtau = 0.01

        dt = time_tracker.compute_dt(dpsi_dtau, dtau, method='mean_derivative')

        # Expected: mean(|dpsi_dtau|) * dtau = 0.5 * 0.01 = 0.005
        assert np.isclose(dt, 0.005)

    def test_compute_dt_rms_derivative(self):
        """Test dt computation with RMS derivative method."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Create mock derivative with varying magnitudes
        dpsi_dtau = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0], dtype=complex)
        dtau = 0.01

        dt = time_tracker.compute_dt(dpsi_dtau, dtau, method='rms_derivative')

        # Expected: √(mean(|dpsi_dtau|²)) * dtau
        expected_rms = np.sqrt(np.mean(np.abs(dpsi_dtau) ** 2))
        expected_dt = expected_rms * dtau

        assert np.isclose(dt, expected_dt)

    def test_dt_always_positive(self):
        """Test that dt is always positive."""
        manifold = PreGeometricManifold(N_nodes=10, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Try various dpsi_dtau
        for _ in range(10):
            dpsi_dtau = (np.random.randn(10) + 1j * np.random.randn(10)) * 0.5
            dt = time_tracker.compute_dt(dpsi_dtau, 0.01)
            assert dt >= 0

    def test_dt_scales_with_dtau(self):
        """Test that dt scales linearly with dtau."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        dpsi_dtau = np.ones(8, dtype=complex) * 0.5

        dt1 = time_tracker.compute_dt(dpsi_dtau, 0.01)
        dt2 = time_tracker.compute_dt(dpsi_dtau, 0.02)

        # Should be linear: dt2 / dt1 = 2
        assert np.isclose(dt2 / dt1, 2.0)

    def test_local_time_rate(self):
        """Test local time rate computation."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        dpsi_dtau = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0], dtype=complex)

        rates = time_tracker.local_time_rate(dpsi_dtau)

        # Should return |dpsi_dtau|
        expected = np.abs(dpsi_dtau)
        assert np.allclose(rates, expected)

    def test_time_dilation_factor(self):
        """Test relative time dilation between nodes."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Node 0: rate = 1.0, Node 1: rate = 2.0
        dpsi_dtau = np.array([1.0, 2.0, 1.5, 0.5, 1.0, 1.0, 1.0, 1.0], dtype=complex)

        alpha_01 = time_tracker.time_dilation_factor(dpsi_dtau, 0, 1)
        alpha_10 = time_tracker.time_dilation_factor(dpsi_dtau, 1, 0)

        # Node 0 has half the rate of node 1
        assert np.isclose(alpha_01, 0.5)
        assert np.isclose(alpha_10, 2.0)
        assert np.isclose(alpha_01 * alpha_10, 1.0)

    def test_time_dilation_zero_rate(self):
        """Test time dilation when one node has zero rate."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        dpsi_dtau = np.array([1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=complex)

        alpha = time_tracker.time_dilation_factor(dpsi_dtau, 0, 1)

        # Node 1 has zero rate, so alpha should be inf
        assert np.isinf(alpha)

    def test_integrate_time_simple(self):
        """Test time integration over simple trajectory."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Constant derivative over 10 steps
        dpsi_dtau_list = [np.ones(8, dtype=complex) * 0.5 for _ in range(10)]
        dtau = 0.01

        total_age, time_array = time_tracker.integrate_time(dpsi_dtau_list, dtau)

        # Expected: 10 steps * 0.5 * 0.01 = 0.05
        assert np.isclose(total_age, 0.05)
        assert len(time_array) == 11  # n_steps + 1
        assert time_array[0] == 0.0
        assert time_array[-1] == total_age

    def test_integrate_time_monotonic(self):
        """Test that integrated time is monotonically increasing."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Random derivatives (all positive magnitudes)
        rng = np.random.default_rng(42)
        dpsi_dtau_list = [
            rng.random(8) + 1j * rng.random(8)
            for _ in range(20)
        ]
        dtau = 0.01

        _, time_array = time_tracker.integrate_time(dpsi_dtau_list, dtau)

        # Check monotonicity
        diffs = np.diff(time_array)
        assert np.all(diffs >= 0), "Time must be monotonically increasing"

    def test_integrate_time_reproducibility(self):
        """Test that time integration is reproducible."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Same random seed should give same result
        rng1 = np.random.default_rng(999)
        dpsi_dtau_list1 = [rng1.random(8) + 1j * rng1.random(8) for _ in range(10)]

        rng2 = np.random.default_rng(999)
        dpsi_dtau_list2 = [rng2.random(8) + 1j * rng2.random(8) for _ in range(10)]

        total_age1, _ = time_tracker.integrate_time(dpsi_dtau_list1, 0.01)
        total_age2, _ = time_tracker.integrate_time(dpsi_dtau_list2, 0.01)

        assert np.isclose(total_age1, total_age2)

    def test_check_causality(self):
        """Test causality verification."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Create mock trajectory
        psi_trajectory = [field.psi.copy() for _ in range(5)]
        dpsi_dtau_list = [np.ones(8, dtype=complex) * 0.5 for _ in range(5)]

        report = time_tracker.check_causality(psi_trajectory, dpsi_dtau_list)

        assert report['is_causal'] is True
        assert report['local_violations'] == 0

    def test_compute_time_statistics(self):
        """Test time statistics computation."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        # Create trajectory with varying rates
        dpsi_dtau_list = [
            np.ones(8, dtype=complex) * (0.5 + 0.1 * k)
            for k in range(10)
        ]
        dtau = 0.01

        stats = time_tracker.compute_time_statistics(dpsi_dtau_list, dtau)

        assert 'total_age' in stats
        assert 'mean_dt_per_step' in stats
        assert 'dt_variation' in stats
        assert 'min_time_rate' in stats
        assert 'max_time_rate' in stats
        assert 'time_dilation_range' in stats
        assert stats['n_steps'] == 10

    def test_compare_with_tau(self):
        """Test comparison of physical time with evolution parameter."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random()

        time_tracker = EmergentTime(field)

        dpsi_dtau_list = [np.ones(8, dtype=complex) * 2.0 for _ in range(10)]
        dtau = 0.01

        comparison = time_tracker.compare_with_tau(dpsi_dtau_list, dtau)

        assert 'total_physical_time' in comparison
        assert 'total_parameter_time' in comparison
        assert 'ratio_T_over_tau' in comparison

        # Total tau = 10 * 0.01 = 0.1
        assert np.isclose(comparison['total_parameter_time'], 0.1)

        # Ratio should be ~2.0 (since |dpsi/dtau| = 2.0)
        assert np.isclose(comparison['ratio_T_over_tau'], 2.0)

    def test_repr(self):
        """Test string representation."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        time_tracker = EmergentTime(field)

        repr_str = repr(time_tracker)
        assert 'EmergentTime' in repr_str
        assert '8' in repr_str

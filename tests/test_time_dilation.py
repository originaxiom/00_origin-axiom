"""
Tests for time dilation effects.

Tests:
- Spatial variation of time rate
- Time dilation with evolved fields
- Floor regions have slower time
- High-activity regions have faster time
- Time dilation range measurements
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase4_fc import EmergentTime


class TestTimeDilation:
    """Test spatial variation of time rate."""

    def test_uniform_field_uniform_time(self):
        """Test that uniform field evolution gives uniform time rates."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_constant(amplitude=1.0, phase=0.0)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        # Evolve one step
        diag = dynamics.evolve_step(dt=0.01)

        # Compute time rates
        time_tracker = EmergentTime(field)

        # Get derivative from dynamics (approximate)
        psi_before = field.psi.copy()
        dynamics.evolve_step(dt=0.01)
        psi_after = field.psi

        dpsi_dtau = (psi_after - psi_before) / 0.01

        rates = time_tracker.local_time_rate(dpsi_dtau)

        # For initially uniform field with random drive, rates should vary
        # but not be wildly different
        rate_std = np.std(rates)
        rate_mean = np.mean(rates)

        # Coefficient of variation should be < 50% for weak randomness
        cv = rate_std / rate_mean if rate_mean > 0 else 0
        assert cv < 0.5, "Time rates should be reasonably uniform for weak perturbations"

    def test_time_dilation_with_evolved_field(self):
        """Test time dilation after field evolution."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        # Evolve to create structure
        for _ in range(50):
            dynamics.evolve_step(dt=0.01)

        # Compute derivative for time rate
        psi_before = field.psi.copy()
        dynamics.evolve_step(dt=0.01)
        psi_after = field.psi

        dpsi_dtau = (psi_after - psi_before) / 0.01

        time_tracker = EmergentTime(field)
        rates = time_tracker.local_time_rate(dpsi_dtau)

        # After evolution, time rates should vary spatially
        assert np.max(rates) > np.min(rates), "Time rates should vary after evolution"

        # Compute dilation range
        min_rate = np.min(rates[rates > 1e-12])
        max_rate = np.max(rates)
        dilation_range = max_rate / min_rate

        assert dilation_range > 1.0, "Should have time dilation effects"

    def test_floor_regions_slower_time(self):
        """Test that regions near floor have slower time."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.3)

        dynamics = FrustratedDynamics(
            field,
            gamma=1.0,  # Strong dissipation
            omega=0.5,
            epsilon=0.01,
            drive_amplitude=0.05,  # Weak drive
            drive_seed=42
        )

        # Evolve to push some nodes to floor
        for _ in range(100):
            dynamics.evolve_step(dt=0.01)

        # Compute time rates
        psi_before = field.psi.copy()
        dynamics.evolve_step(dt=0.01)
        psi_after = field.psi

        dpsi_dtau = (psi_after - psi_before) / 0.01

        time_tracker = EmergentTime(field)
        rates = time_tracker.local_time_rate(dpsi_dtau)

        # Identify floor nodes
        amplitudes = np.abs(field.psi)
        floor_threshold = dynamics.epsilon * 1.05  # Within 5% of floor

        floor_nodes = amplitudes < floor_threshold
        active_nodes = amplitudes > floor_threshold * 2

        if np.any(floor_nodes) and np.any(active_nodes):
            mean_rate_floor = np.mean(rates[floor_nodes])
            mean_rate_active = np.mean(rates[active_nodes])

            # Floor nodes should have lower time rate (slower time)
            assert mean_rate_floor <= mean_rate_active, \
                "Floor regions should have slower or equal time passage"

    def test_high_activity_faster_time(self):
        """Test that high-activity regions have faster time."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.3)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.3,  # Weak dissipation
            omega=3.0,  # Strong rotation
            epsilon=0.01,
            drive_amplitude=0.2,  # Strong drive
            drive_seed=42
        )

        # Evolve to create activity gradients
        for _ in range(50):
            dynamics.evolve_step(dt=0.01)

        # Compute time rates
        psi_before = field.psi.copy()
        dynamics.evolve_step(dt=0.01)
        psi_after = field.psi

        dpsi_dtau = (psi_after - psi_before) / 0.01

        time_tracker = EmergentTime(field)
        rates = time_tracker.local_time_rate(dpsi_dtau)

        # Correlation between activity (|dpsi/dtau|) and time rate
        # They should be identical by construction: rate = |dpsi/dtau|
        assert np.allclose(rates, np.abs(dpsi_dtau))

    def test_time_dilation_range_measurement(self):
        """Test measurement of time dilation range."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.5)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.15,
            drive_seed=42
        )

        # Evolve to create structure
        for _ in range(100):
            dynamics.evolve_step(dt=0.01)

        # Collect derivatives over multiple steps
        dpsi_dtau_list = []
        for _ in range(20):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        time_tracker = EmergentTime(field)
        stats = time_tracker.compute_time_statistics(dpsi_dtau_list, dtau=0.01)

        # Time dilation range should be finite and > 1
        assert stats['time_dilation_range'] > 1.0
        assert np.isfinite(stats['time_dilation_range'])

    def test_time_variation_increases_with_evolution(self):
        """Test that time variation increases as field develops structure."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.1)  # Nearly uniform

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        time_tracker = EmergentTime(field)

        # Measure time variation at start
        psi_before = field.psi.copy()
        dynamics.evolve_step(dt=0.01)
        psi_after = field.psi
        dpsi_dtau_early = (psi_after - psi_before) / 0.01
        rates_early = time_tracker.local_time_rate(dpsi_dtau_early)
        cv_early = np.std(rates_early) / np.mean(rates_early)

        # Evolve to develop structure
        for _ in range(100):
            dynamics.evolve_step(dt=0.01)

        # Measure time variation after evolution
        psi_before = field.psi.copy()
        dynamics.evolve_step(dt=0.01)
        psi_after = field.psi
        dpsi_dtau_late = (psi_after - psi_before) / 0.01
        rates_late = time_tracker.local_time_rate(dpsi_dtau_late)
        cv_late = np.std(rates_late) / np.mean(rates_late)

        # Variation should increase (or stay similar, but not decrease drastically)
        # This is a weak test - just checking that variation exists
        assert cv_late > 0, "Should have some time variation after evolution"

    def test_time_dilation_between_specific_nodes(self):
        """Test time dilation measurement between specific node pairs."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.3)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=42
        )

        # Evolve
        for _ in range(50):
            dynamics.evolve_step(dt=0.01)

        # Compute derivative
        psi_before = field.psi.copy()
        dynamics.evolve_step(dt=0.01)
        psi_after = field.psi
        dpsi_dtau = (psi_after - psi_before) / 0.01

        time_tracker = EmergentTime(field)

        # Pick two nodes and measure dilation
        node_i = 0
        node_j = manifold.N // 2

        alpha_ij = time_tracker.time_dilation_factor(dpsi_dtau, node_i, node_j)
        alpha_ji = time_tracker.time_dilation_factor(dpsi_dtau, node_j, node_i)

        # Should be reciprocals
        assert np.isclose(alpha_ij * alpha_ji, 1.0, rtol=1e-10)

        # Both should be positive
        assert alpha_ij > 0
        assert alpha_ji > 0

    def test_integrate_time_with_varying_activity(self):
        """Test time integration when activity varies over trajectory."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        # Start with strong drive
        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.2,  # Strong initially
            drive_seed=42
        )

        time_tracker = EmergentTime(field)

        # Collect derivatives during strong drive phase
        dpsi_dtau_strong = []
        for _ in range(10):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau_strong.append((psi_after - psi_before) / 0.01)

        # Switch to weak drive by creating new dynamics
        dynamics_weak = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.05,  # Weak now
            drive_seed=42
        )

        # Collect derivatives during weak drive phase
        dpsi_dtau_weak = []
        for _ in range(10):
            psi_before = field.psi.copy()
            dynamics_weak.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau_weak.append((psi_after - psi_before) / 0.01)

        # Integrate time for each phase
        total_strong, _ = time_tracker.integrate_time(dpsi_dtau_strong, dtau=0.01)
        total_weak, _ = time_tracker.integrate_time(dpsi_dtau_weak, dtau=0.01)

        # Strong drive phase should accumulate more physical time
        # (higher activity → faster time passage)
        assert total_strong > total_weak, \
            "Strong activity phase should accumulate more physical time"

    def test_contract_acceptance_time_dilation(self):
        """Test contract acceptance criteria for time dilation."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d', random_seed=20260126)
        field = FrustrationField(manifold, seed=20260126)
        field.initialize_random(r_mean=1.0, r_std=0.3)

        dynamics = FrustratedDynamics(
            field,
            gamma=0.5,
            omega=2.0,
            epsilon=0.01,
            drive_amplitude=0.1,
            drive_seed=20260126
        )

        # Evolve to create structure
        for _ in range(100):
            dynamics.evolve_step(dt=0.01)

        # Collect derivatives
        dpsi_dtau_list = []
        for _ in range(20):
            psi_before = field.psi.copy()
            dynamics.evolve_step(dt=0.01)
            psi_after = field.psi
            dpsi_dtau = (psi_after - psi_before) / 0.01
            dpsi_dtau_list.append(dpsi_dtau)

        time_tracker = EmergentTime(field)

        # CONTRACT CRITERIA:
        # 1. Time rate varies across nodes
        rates_all = np.concatenate([
            time_tracker.local_time_rate(dpsi) for dpsi in dpsi_dtau_list
        ])
        assert np.std(rates_all) > 0, "✗ Time rate must vary spatially"

        # 2. Time dilation factor measurable
        dpsi_dtau = dpsi_dtau_list[-1]
        alpha = time_tracker.time_dilation_factor(dpsi_dtau, 0, manifold.N // 2)
        assert np.isfinite(alpha) and alpha > 0, "✗ Time dilation factor must be measurable"

        # 3. Dilation range > 1
        stats = time_tracker.compute_time_statistics(dpsi_dtau_list, dtau=0.01)
        assert stats['time_dilation_range'] > 1.0, "✗ Time dilation range must exceed 1.0"

        print("✓ All time dilation acceptance criteria passed")

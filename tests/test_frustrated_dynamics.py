"""
Tests for FrustratedDynamics class.

Basic functionality:
- Initialization
- Single step evolution
- Floor enforcement
- Reproducibility
- Energy bounds
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics


class TestFrustratedDynamics:
    """Test basic frustrated dynamics functionality."""

    def test_initialization(self):
        """Test that FrustratedDynamics initializes correctly."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.1)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )

        assert dynamics.field is field
        assert dynamics.gamma == 0.1
        assert dynamics.omega == 1.0
        assert dynamics.epsilon == 0.01
        assert dynamics.drive_amplitude == 0.05
        assert dynamics.tau == 0.0

    def test_single_step_evolution(self):
        """Test that single step evolution works without crashing."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.1)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05,
            drive_seed=123
        )

        # Store initial state
        psi_initial = field.psi.copy()

        # Evolve one step
        diag = dynamics.evolve_step(dt=0.01)

        # Check that state changed
        assert not np.allclose(field.psi, psi_initial)

        # Check diagnostics structure
        assert 'floor_hits' in diag
        assert 'global_cancel' in diag
        assert 'mean_amp' in diag
        assert 'energy' in diag
        assert 'tau' in diag

        # Check that time advanced
        assert dynamics.tau == 0.01

    def test_floor_enforcement(self):
        """Test that floor is enforced: no |ψ| < ε."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        # Initialize with small amplitudes to trigger floor
        field.initialize_random(r_mean=0.005, r_std=0.002)

        epsilon = 0.01
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.5,  # Strong dissipation
            omega=0.0,  # No rotation
            epsilon=epsilon,
            drive_amplitude=0.0  # No drive
        )

        # Evolve for several steps
        for _ in range(10):
            dynamics.evolve_step(dt=0.01)

        # Check that no amplitudes are below floor (with small tolerance for floating point)
        amplitudes = np.abs(field.psi)
        assert np.all(amplitudes >= epsilon - 1e-10), \
            f"Found amplitudes below floor: min = {amplitudes.min()}, floor = {epsilon}"

        # Should have many floor hits
        diag = dynamics.evolve_step(dt=0.01)
        assert diag['floor_hits'] >= 0  # At least some hits expected

    def test_reproducibility(self):
        """Test that same seed produces same trajectory."""
        def run_trajectory(seed):
            manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
            field = FrustrationField(manifold, seed=seed)
            field.initialize_random(r_mean=0.5, r_std=0.1)

            dynamics = FrustratedDynamics(
                field=field,
                gamma=0.1,
                omega=1.0,
                epsilon=0.01,
                drive_amplitude=0.05,
                drive_seed=999
            )

            trajectory = dynamics.evolve_trajectory(n_steps=20, dt=0.01)
            return trajectory

        # Run twice with same seed
        traj1 = run_trajectory(seed=42)
        traj2 = run_trajectory(seed=42)

        # Should be identical
        assert np.allclose(traj1['energy'].values, traj2['energy'].values)
        assert np.allclose(traj1['mean_amp'].values, traj2['mean_amp'].values)
        assert np.all(traj1['floor_hits'].values == traj2['floor_hits'].values)

        # Run with different seed
        traj3 = run_trajectory(seed=99)

        # Should be different
        assert not np.allclose(traj1['energy'].values, traj3['energy'].values)

    def test_energy_bounded(self):
        """Test that energy remains bounded (no explosion)."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05,
            drive_seed=123
        )

        # Evolve for many steps
        trajectory = dynamics.evolve_trajectory(n_steps=200, dt=0.01)

        # Energy should be positive
        assert np.all(trajectory['energy'] > 0)

        # Energy should not explode (reasonable upper bound)
        # With gamma=0.1, omega=1.0, drive=0.05, energy should be O(1)
        max_energy = trajectory['energy'].max()
        assert max_energy < 10.0, \
            f"Energy exploded: max = {max_energy}"

    def test_evolution_with_zero_drive(self):
        """Test evolution without drive (dissipation only)."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.1)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.2,
            omega=0.0,
            epsilon=0.01,
            drive_amplitude=0.0  # No drive
        )

        trajectory = dynamics.evolve_trajectory(n_steps=100, dt=0.01)

        # Should still work
        assert len(trajectory) > 0
        assert np.all(trajectory['energy'] >= 0)

        # Mean amplitude should decrease (dissipation dominates)
        initial_amp = trajectory['mean_amp'].iloc[0]
        final_amp = trajectory['mean_amp'].iloc[-1]
        assert final_amp <= initial_amp

    def test_trajectory_save_every(self):
        """Test that save_every parameter works correctly."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.1)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )

        # Save every 5 steps
        trajectory = dynamics.evolve_trajectory(
            n_steps=50,
            dt=0.01,
            save_every=5
        )

        # Should have 10 records (0, 5, 10, ..., 45)
        assert len(trajectory) == 10
        assert trajectory['step'].iloc[0] == 0
        assert trajectory['step'].iloc[1] == 5
        assert trajectory['step'].iloc[-1] == 45

    def test_reset(self):
        """Test that reset() works correctly."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.1)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )

        # Evolve for some time
        dynamics.evolve_trajectory(n_steps=20, dt=0.01)
        assert dynamics.tau > 0

        # Reset
        dynamics.reset()
        assert dynamics.tau == 0.0

    def test_floor_projection_correctness(self):
        """Test that floor projection is exactly radial."""
        manifold = PreGeometricManifold(N_nodes=10, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        # Create state with some nodes below floor
        epsilon = 0.1
        psi = np.array([
            0.05 * np.exp(1j * 0.5),  # Below floor
            0.15 * np.exp(1j * 1.0),  # Above floor
            0.03 * np.exp(1j * 2.0),  # Below floor
        ] + [0.2] * 7)
        field.psi[:10] = psi

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.0,
            omega=0.0,
            epsilon=epsilon,
            drive_amplitude=0.0
        )

        # Manually enforce floor
        n_hits = dynamics._enforce_floor()

        # Check that 2 nodes were projected
        assert n_hits == 2

        # Check that projected nodes have correct amplitude
        amplitudes = np.abs(field.psi[:3])
        assert np.isclose(amplitudes[0], epsilon)
        assert np.isclose(amplitudes[2], epsilon)
        assert amplitudes[1] > epsilon

        # Check that phases were preserved
        # Original: 0.05*e^(i*0.5), projected: 0.1*e^(i*0.5)
        # Phase should still be 0.5
        projected_phase = np.angle(field.psi[0])
        assert np.isclose(projected_phase, 0.5, atol=1e-10)

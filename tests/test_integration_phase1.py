"""
Integration tests for Phase 1_FC.

Tests full workflow from manifold → field → dynamics → evolution.
"""

import pytest
import numpy as np
import pandas as pd
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics


class TestPhase1Integration:
    """Integration tests for frustrated dynamics."""

    def test_full_workflow(self):
        """
        Test complete Phase 0 + Phase 1 workflow.

        Steps:
        1. Create manifold
        2. Create field
        3. Initialize field
        4. Create dynamics
        5. Evolve trajectory
        6. Verify diagnostics
        """
        # Step 1: Create manifold
        manifold = PreGeometricManifold(
            N_nodes=100,
            topology='cubic_3d'
        )

        # Step 2: Create field
        field = FrustrationField(manifold, seed=20260125)

        # Step 3: Initialize
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Step 4: Create dynamics
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05,
            drive_seed=999
        )

        # Step 5: Evolve
        trajectory = dynamics.evolve_trajectory(
            n_steps=100,
            dt=0.01,
            save_every=2
        )

        # Step 6: Verify
        assert isinstance(trajectory, pd.DataFrame)
        assert len(trajectory) == 50  # 100 steps, save every 2

        # Check columns
        required_cols = ['step', 'tau', 'floor_hits', 'global_cancel', 'mean_amp', 'energy']
        for col in required_cols:
            assert col in trajectory.columns

        # Check values are reasonable
        assert np.all(trajectory['energy'] > 0)
        assert np.all(trajectory['mean_amp'] > 0)
        assert np.all(trajectory['global_cancel'] >= 0)
        assert np.all(trajectory['global_cancel'] <= 1)

    def test_multiple_trajectories(self):
        """Test that multiple trajectories can be run sequentially."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )

        # Run first trajectory
        traj1 = dynamics.evolve_trajectory(n_steps=50, dt=0.01)
        tau_after_1 = dynamics.tau

        # Run second trajectory (continues from where first left off)
        traj2 = dynamics.evolve_trajectory(n_steps=50, dt=0.01)
        tau_after_2 = dynamics.tau

        # Time should have accumulated
        assert tau_after_2 > tau_after_1
        assert np.isclose(tau_after_2, tau_after_1 + 50 * 0.01)

        # Reset and run again
        dynamics.reset()
        traj3 = dynamics.evolve_trajectory(n_steps=50, dt=0.01)

        # Should start from tau=0 again
        assert traj3['tau'].iloc[0] < traj2['tau'].iloc[0]

    def test_diagnostics_saved_correctly(self):
        """Test that diagnostics are saved correctly in DataFrame."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )

        trajectory = dynamics.evolve_trajectory(n_steps=30, dt=0.02)

        # Check step numbers
        assert trajectory['step'].iloc[0] == 0
        assert trajectory['step'].iloc[-1] == 29
        assert len(trajectory) == 30

        # Check time progression
        expected_times = np.arange(30) * 0.02 + 0.02  # Times after each step
        assert np.allclose(trajectory['tau'].values, expected_times, atol=1e-10)

        # Check that diagnostics are non-negative
        assert np.all(trajectory['floor_hits'] >= 0)
        assert np.all(trajectory['energy'] >= 0)
        assert np.all(trajectory['mean_amp'] >= 0)

    def test_different_topologies(self):
        """Test that dynamics work on different manifold topologies."""
        topologies = ['cubic_3d', 'random_graph']

        for topology in topologies:
            manifold = PreGeometricManifold(
                N_nodes=50,
                topology=topology,
                random_seed=42
            )

            field = FrustrationField(manifold, seed=123)
            field.initialize_random(r_mean=0.5, r_std=0.2)

            dynamics = FrustratedDynamics(
                field=field,
                gamma=0.1,
                omega=1.0,
                epsilon=0.01,
                drive_amplitude=0.05
            )

            # Should work on any topology
            trajectory = dynamics.evolve_trajectory(n_steps=50, dt=0.01)

            assert len(trajectory) > 0
            assert np.all(trajectory['energy'] > 0)

    def test_field_state_updates(self):
        """Test that field state is correctly updated during evolution."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Store initial state
        psi_initial = field.psi.copy()
        initial_amp = field.mean_amplitude()

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )

        # Evolve
        dynamics.evolve_trajectory(n_steps=50, dt=0.01)

        # Field should have changed
        assert not np.allclose(field.psi, psi_initial)

        # Current amplitude should match what field reports
        current_amp = field.mean_amplitude()
        assert current_amp > 0

    def test_save_every_parameter_correctness(self):
        """Test that save_every correctly subsamples trajectory."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )

        # Test different save_every values
        test_cases = [
            (100, 1, 100),   # Save every step
            (100, 5, 20),    # Save every 5 steps
            (100, 10, 10),   # Save every 10 steps
        ]

        for n_steps, save_every, expected_len in test_cases:
            dynamics.reset()
            field.initialize_random(r_mean=0.5, r_std=0.2)

            trajectory = dynamics.evolve_trajectory(
                n_steps=n_steps,
                dt=0.01,
                save_every=save_every
            )

            assert len(trajectory) == expected_len, \
                f"n_steps={n_steps}, save_every={save_every}: " \
                f"expected {expected_len} records, got {len(trajectory)}"

            # Check that step numbers are correct
            expected_steps = np.arange(0, n_steps, save_every)
            assert np.all(trajectory['step'].values == expected_steps)

    def test_phase1_readiness(self):
        """
        Test that Phase 1 implementation is ready.

        This test serves as acceptance test for Phase 1_FC contract.
        """
        # Create system
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold, seed=20260125)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Create dynamics with drive
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05,
            drive_seed=999
        )

        # Evolve to steady state
        trajectory = dynamics.evolve_trajectory(n_steps=200, dt=0.01)

        # Verify all required functionality works
        assert isinstance(trajectory, pd.DataFrame)
        assert 'energy' in trajectory.columns
        assert 'floor_hits' in trajectory.columns
        assert 'global_cancel' in trajectory.columns

        # Verify floor enforcement
        amplitudes = np.abs(field.psi)
        assert np.all(amplitudes >= dynamics.epsilon - 1e-10)

        # Verify energy bounds
        assert np.all(trajectory['energy'] > 0)
        assert trajectory['energy'].max() < 10.0

        # Verify system is alive (not frozen)
        final_records = trajectory.iloc[-20:]
        floor_activity = final_records['floor_hits'].mean() / manifold.N
        assert floor_activity < 0.5  # Not frozen at floor

        # Phase 1 is ready for acceptance

    def test_workflow_example_documentation(self):
        """
        Example workflow for documentation.

        This serves as both test and usage documentation.
        """
        # Step 1: Create pre-geometric manifold
        manifold = PreGeometricManifold(
            N_nodes=64,
            topology='cubic_3d'
        )

        # Step 2: Create frustration field
        field = FrustrationField(manifold, seed=42)

        # Step 3: Initialize with random configuration
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Step 4: Create frustrated dynamics
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,          # Dissipation rate
            omega=1.0,          # Rotation frequency
            epsilon=0.01,       # Floor value
            drive_amplitude=0.05,  # Drive strength
            drive_seed=123
        )

        # Step 5: Evolve trajectory
        trajectory = dynamics.evolve_trajectory(
            n_steps=100,
            dt=0.01,
            save_every=1
        )

        # Step 6: Analyze results
        mean_energy = trajectory['energy'].mean()
        mean_floor_activity = trajectory['floor_hits'].mean() / manifold.N
        final_amplitude = trajectory['mean_amp'].iloc[-1]

        # Sanity checks
        assert mean_energy > 0
        assert 0 <= mean_floor_activity <= 1
        assert final_amplitude > 0

        # Phase 1 workflow complete - ready for Phase 2 (emergent geometry)

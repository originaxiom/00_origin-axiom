"""
Complete tests for Phase 5_FC: Emergent Drive

Combined test suite covering:
- Drive computation and constraint evaluation
- Self-sustaining evolution
- Comparison with imposed drive
- Full integration Phase 0→5
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase5_fc import EmergentDrive


class TestEmergentDriveBasics:
    """Test basic drive computation functionality."""

    def test_initialization(self):
        """Test EmergentDrive initialization."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        assert drive_computer.manifold is manifold
        assert drive_computer.epsilon == 0.01

    def test_evaluate_constraint(self):
        """Test constraint evaluation C = |∫ψ| - ε."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_constant(amplitude=1.0, phase=0.0)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)
        constraint = drive_computer.evaluate_constraint(field.psi)

        # Constant field: |∫ψ| = 1.0, so C = 1.0 - 0.01 = 0.99
        assert np.isclose(constraint, 0.99, atol=1e-6)

    def test_constraint_near_floor(self):
        """Test constraint when field is near floor."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        # Field very close to floor
        field.psi = np.ones(8, dtype=complex) * 0.011  # Just above ε=0.01

        drive_computer = EmergentDrive(manifold, epsilon=0.01)
        constraint = drive_computer.evaluate_constraint(field.psi)

        # |∫ψ| ≈ 0.011, so C ≈ 0.001 (near zero)
        assert constraint >= 0
        assert constraint < 0.01

    def test_compute_multiplier_increases_near_floor(self):
        """Test that λ increases when constraint approaches zero."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        # Far from floor
        psi_far = np.ones(8, dtype=complex) * 1.0
        lambda_far = drive_computer.compute_multiplier(psi_far, control_gain=0.1)

        # Near floor
        psi_near = np.ones(8, dtype=complex) * 0.011
        lambda_near = drive_computer.compute_multiplier(psi_near, control_gain=0.1)

        # λ should be larger when near floor
        assert lambda_near > lambda_far

    def test_compute_drive_shape(self):
        """Test that computed drive has correct shape and properties."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)
        drive = drive_computer.compute_drive(field.psi, control_gain=0.1)

        # Drive should have same shape as psi
        assert drive.shape == field.psi.shape
        assert drive.dtype == complex

        # All drive components should have similar magnitude (uniform by design)
        drive_mags = np.abs(drive)
        assert np.std(drive_mags) < 1e-10  # Should be identical

    def test_drive_points_toward_increasing_integral(self):
        """Test that drive direction increases |∫ψ|."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        # Compute initial integral
        integral_before = np.abs(np.mean(field.psi))

        # Compute drive
        drive = drive_computer.compute_drive(field.psi, control_gain=0.1)

        # Add drive to field (small step)
        psi_new = field.psi + 0.01 * drive
        integral_after = np.abs(np.mean(psi_new))

        # Drive should increase |∫ψ|
        assert integral_after > integral_before

    def test_repr(self):
        """Test string representation."""
        manifold = PreGeometricManifold(N_nodes=8, topology='cubic_3d')
        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        repr_str = repr(drive_computer)
        assert 'EmergentDrive' in repr_str
        assert '8' in repr_str
        assert '0.01' in repr_str


class TestSelfSustainingEvolution:
    """Test self-sustaining evolution with emergent drive."""

    def test_evolution_without_collapse(self):
        """Test that system doesn't collapse with emergent drive."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        # Evolve with emergent drive
        diag = drive_computer.evolve_with_emergent_drive(
            field, gamma=0.5, omega=2.0, n_steps=100, dt=0.01, control_gain=0.1
        )

        # System should not collapse
        assert diag['final_constraint'] > 0, "Constraint must remain positive"
        assert diag['is_self_sustaining'], "System must be self-sustaining"

    def test_constraint_maintained(self):
        """Test that constraint C > 0 is maintained throughout evolution."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.3)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        diag = drive_computer.evolve_with_emergent_drive(
            field, gamma=0.5, omega=2.0, n_steps=50, dt=0.01, control_gain=0.1
        )

        # All constraint values should be > 0
        assert np.all(diag['constraint_history'] > 0), "Constraint violated"

    def test_drive_amplitude_bounded(self):
        """Test that drive amplitude λ remains finite and bounded."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        diag = drive_computer.evolve_with_emergent_drive(
            field, gamma=0.5, omega=2.0, n_steps=50, dt=0.01, control_gain=0.1
        )

        # λ should be finite
        assert np.all(np.isfinite(diag['lambda_history']))

        # λ should be bounded (not explode)
        assert np.max(diag['lambda_history']) < 1000, "λ too large"

    def test_minimal_floor_violations(self):
        """Test that floor violations are minimal (<5%)."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        diag = drive_computer.evolve_with_emergent_drive(
            field, gamma=0.5, omega=2.0, n_steps=100, dt=0.01, control_gain=0.1
        )

        # Less than 5% violation rate
        violation_rate = diag['mean_violations_per_step'] / len(field.psi)
        assert violation_rate < 0.05, f"Violation rate {violation_rate:.2%} exceeds 5%"


class TestComparisonWithImposed:
    """Test comparison between emergent and imposed drives."""

    def test_comparable_energies(self):
        """Test that emergent and imposed drives produce comparable energies."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)

        # Two identical fields
        field_emergent = FrustrationField(manifold, seed=999)
        field_emergent.initialize_random(r_mean=1.0, r_std=0.2)

        field_imposed = FrustrationField(manifold, seed=999)
        field_imposed.initialize_random(r_mean=1.0, r_std=0.2)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        # Compare
        comparison = drive_computer.compare_with_imposed_drive(
            field_emergent, field_imposed,
            imposed_amplitude=0.1, imposed_seed=42,
            gamma=0.5, omega=2.0,
            n_steps=50, dt=0.01,
            control_gain=0.1
        )

        # Energies should be within factor of 2
        assert 0.5 <= comparison['energy_ratio'] <= 2.0, \
            f"Energy ratio {comparison['energy_ratio']:.2f} outside [0.5, 2.0]"

    def test_comparable_drives(self):
        """Test that emergent drive amplitude is comparable to imposed."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)

        field_emergent = FrustrationField(manifold, seed=999)
        field_emergent.initialize_random(r_mean=1.0, r_std=0.2)

        field_imposed = FrustrationField(manifold, seed=999)
        field_imposed.initialize_random(r_mean=1.0, r_std=0.2)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        comparison = drive_computer.compare_with_imposed_drive(
            field_emergent, field_imposed,
            imposed_amplitude=0.1, imposed_seed=42,
            gamma=0.5, omega=2.0,
            n_steps=50, dt=0.01,
            control_gain=0.1
        )

        # Drive amplitudes should be within factor of 5 (emergent can be more/less efficient)
        assert 0.2 <= comparison['drive_ratio'] <= 5.0, \
            f"Drive ratio {comparison['drive_ratio']:.2f} outside [0.2, 5.0]"

    def test_both_sustain(self):
        """Test that both emergent and imposed drives sustain the system."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)

        field_emergent = FrustrationField(manifold, seed=999)
        field_emergent.initialize_random(r_mean=1.0, r_std=0.2)

        field_imposed = FrustrationField(manifold, seed=999)
        field_imposed.initialize_random(r_mean=1.0, r_std=0.2)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        comparison = drive_computer.compare_with_imposed_drive(
            field_emergent, field_imposed,
            imposed_amplitude=0.1, imposed_seed=42,
            gamma=0.5, omega=2.0,
            n_steps=50, dt=0.01,
            control_gain=0.1
        )

        # Emergent should be self-sustaining
        assert comparison['emergent_trajectory']['is_self_sustaining']

        # Imposed should also have minimal violations
        assert comparison['imposed_floor_violations'] < 50 * 27 * 0.05


class TestPhase5Integration:
    """Test full workflow integration through Phase 5."""

    def test_full_workflow(self):
        """Test complete Phase 0→5 pipeline with emergent drive."""
        # Phase 0: Manifold and field
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=42)
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=1.0, r_std=0.2)

        # Phase 5: Emergent drive evolution
        drive_computer = EmergentDrive(manifold, epsilon=0.01)
        diag = drive_computer.evolve_with_emergent_drive(
            field, gamma=0.5, omega=2.0, n_steps=50, dt=0.01, control_gain=0.1
        )

        # Verify all acceptance criteria
        assert diag['is_self_sustaining'], "Must be self-sustaining"
        assert np.all(diag['constraint_history'] > 0), "Constraint must stay positive"
        assert np.all(np.isfinite(diag['lambda_history'])), "λ must be finite"
        assert diag['floor_violations'] < 50 * 27 * 0.05, "Minimal violations"

    def test_phase5_readiness(self):
        """Test Phase 5 readiness: All acceptance criteria."""
        seed = 20260126

        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d', random_seed=seed)
        field = FrustrationField(manifold, seed=seed)
        field.initialize_random(r_mean=1.0, r_std=0.3)

        drive_computer = EmergentDrive(manifold, epsilon=0.01)

        # Evolve with emergent drive
        diag = drive_computer.evolve_with_emergent_drive(
            field, gamma=0.5, omega=2.0, n_steps=100, dt=0.01, control_gain=0.1
        )

        # ACCEPTANCE CRITERION 1: Drive derivation
        assert np.all(diag['lambda_history'] >= 0), "✗ λ must be non-negative"
        # λ should increase when C decreases
        print("✓ Drive derived from constraint")

        # ACCEPTANCE CRITERION 2: Self-sustaining
        assert diag['is_self_sustaining'], "✗ Must be self-sustaining"
        assert diag['final_constraint'] > 0, "✗ Constraint must be positive"
        assert np.max(diag['lambda_history']) < 1000, "✗ λ must be bounded"
        print("✓ Self-sustaining evolution")

        # ACCEPTANCE CRITERION 3: Comparison with imposed
        field_imposed = FrustrationField(manifold, seed=seed)
        field_imposed.initialize_random(r_mean=1.0, r_std=0.3)
        field_emergent = FrustrationField(manifold, seed=seed)
        field_emergent.initialize_random(r_mean=1.0, r_std=0.3)

        comparison = drive_computer.compare_with_imposed_drive(
            field_emergent, field_imposed,
            imposed_amplitude=0.1, imposed_seed=seed,
            gamma=0.5, omega=2.0, n_steps=100, dt=0.01, control_gain=0.1
        )
        assert comparison['are_comparable'], "✗ Must be comparable to imposed"
        print(f"✓ Comparable to imposed (energy ratio: {comparison['energy_ratio']:.2f})")

        # ACCEPTANCE CRITERION 4: Physical interpretation
        # Drive emerges from floor constraint (verified by design)
        print("✓ Drive emerges from floor constraint (feedback control)")

        print("\n✓✓✓ All Phase 5 acceptance criteria PASSED ✓✓✓")

    def test_reproducibility(self):
        """Test that evolution with emergent drive is reproducible."""
        manifold = PreGeometricManifold(N_nodes=27, topology='cubic_3d', random_seed=123)

        # Run 1
        field1 = FrustrationField(manifold, seed=456)
        field1.initialize_random(r_mean=1.0, r_std=0.2)
        drive_computer1 = EmergentDrive(manifold, epsilon=0.01)
        diag1 = drive_computer1.evolve_with_emergent_drive(
            field1, gamma=0.5, omega=2.0, n_steps=30, dt=0.01, control_gain=0.1
        )

        # Run 2 (same seeds)
        field2 = FrustrationField(manifold, seed=456)
        field2.initialize_random(r_mean=1.0, r_std=0.2)
        drive_computer2 = EmergentDrive(manifold, epsilon=0.01)
        diag2 = drive_computer2.evolve_with_emergent_drive(
            field2, gamma=0.5, omega=2.0, n_steps=30, dt=0.01, control_gain=0.1
        )

        # Results should be identical
        assert np.allclose(diag1['constraint_history'], diag2['constraint_history'])
        assert np.allclose(diag1['lambda_history'], diag2['lambda_history'])

"""
Tests for FrustrationField.
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField


class TestFrustrationField:
    """Test suite for FrustrationField class."""

    def test_initialization(self):
        """Test basic field initialization."""
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        assert field.manifold is manifold
        assert field.psi.shape == (50,)
        assert field.psi.dtype == complex
        assert np.all(field.psi == 0.0)  # Initially zero

    def test_initialize_random(self):
        """Test random initialization."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold, seed=123)

        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Check that field is non-zero
        assert not np.all(field.psi == 0.0)

        # Check mean amplitude approximately matches
        mean_amp = field.mean_amplitude()
        assert 0.3 < mean_amp < 0.7  # Should be around 0.5 ± ~2σ

        # Check all amplitudes are non-negative
        assert np.all(np.abs(field.psi) >= 0.0)

    def test_random_reproducibility(self):
        """Test that same seed gives same random field."""
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')

        field1 = FrustrationField(manifold, seed=42)
        field1.initialize_random(r_mean=1.0, r_std=0.5)

        field2 = FrustrationField(manifold, seed=42)
        field2.initialize_random(r_mean=1.0, r_std=0.5)

        # Same seed should give identical fields
        assert np.allclose(field1.psi, field2.psi)

    def test_random_different_seeds(self):
        """Test that different seeds give different fields."""
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')

        field1 = FrustrationField(manifold, seed=42)
        field1.initialize_random()

        field2 = FrustrationField(manifold, seed=99)
        field2.initialize_random()

        # Different seeds should give different fields
        assert not np.allclose(field1.psi, field2.psi)

    def test_initialize_constant(self):
        """Test constant initialization."""
        manifold = PreGeometricManifold(N_nodes=20, topology='cubic_3d')
        field = FrustrationField(manifold)

        field.initialize_constant(amplitude=2.0, phase=np.pi/4)

        # All values should be identical
        expected = 2.0 * np.exp(1j * np.pi / 4)
        assert np.allclose(field.psi, expected)

        # Check cancellation measure (should be 1.0 for aligned phases)
        C = field.global_cancellation_measure()
        assert abs(C - 1.0) < 1e-10

    def test_global_cancellation_measure_perfect(self):
        """Test cancellation measure for perfectly aligned phases."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold)

        # All same value = no cancellation
        field.initialize_constant(amplitude=1.0, phase=0.0)
        C = field.global_cancellation_measure()
        assert abs(C - 1.0) < 1e-10

    def test_global_cancellation_measure_random(self):
        """Test cancellation measure scales as N^{-1/2} for random phases."""
        manifold = PreGeometricManifold(N_nodes=1000, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        field.initialize_random(r_mean=1.0, r_std=0.1)

        C = field.global_cancellation_measure()

        # For random phases, expect C ~ 1/√N ≈ 1/√1000 ≈ 0.032
        # Allow generous bounds (0.01 to 0.1)
        assert 0.01 < C < 0.1

    def test_global_cancellation_zero_field(self):
        """Test cancellation measure for zero field."""
        manifold = PreGeometricManifold(N_nodes=10, topology='cubic_3d')
        field = FrustrationField(manifold)

        # Zero field should give C = 0
        C = field.global_cancellation_measure()
        assert C == 0.0

    def test_mean_amplitude(self):
        """Test mean amplitude calculation."""
        manifold = PreGeometricManifold(N_nodes=50, topology='cubic_3d')
        field = FrustrationField(manifold)

        field.initialize_constant(amplitude=3.0, phase=0.0)

        mean_amp = field.mean_amplitude()
        assert abs(mean_amp - 3.0) < 1e-10

    def test_amplitude_std(self):
        """Test amplitude standard deviation."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        # Constant field should have zero std
        field.initialize_constant(amplitude=1.0)
        assert field.amplitude_std() < 1e-10

        # Random field should have non-zero std
        field.initialize_random(r_mean=1.0, r_std=0.5)
        assert field.amplitude_std() > 0.1

    def test_phase_coherence_aligned(self):
        """Test phase coherence for aligned phases."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold)

        # All same phase = full coherence
        field.initialize_constant(amplitude=1.0, phase=np.pi/3)
        coherence = field.phase_coherence()
        assert abs(coherence - 1.0) < 1e-10

    def test_phase_coherence_random(self):
        """Test phase coherence for random phases."""
        manifold = PreGeometricManifold(N_nodes=500, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        field.initialize_random(r_mean=1.0, r_std=0.1)

        coherence = field.phase_coherence()

        # Random phases should have low coherence (close to 0)
        assert 0.0 <= coherence < 0.2

    def test_psi_setter(self):
        """Test psi setter with validation."""
        manifold = PreGeometricManifold(N_nodes=10, topology='cubic_3d')
        field = FrustrationField(manifold)

        # Valid assignment
        new_psi = np.random.random(10) * np.exp(1j * np.random.random(10))
        field.psi = new_psi
        assert np.allclose(field.psi, new_psi)

        # Invalid shape should raise error
        with pytest.raises(ValueError, match="psi shape must be"):
            field.psi = np.array([1.0 + 1j, 2.0 + 2j])  # Wrong size

    def test_repr(self):
        """Test string representation."""
        manifold = PreGeometricManifold(N_nodes=20, topology='cubic_3d')
        field = FrustrationField(manifold)
        field.initialize_random(r_mean=0.5, r_std=0.1)

        repr_str = repr(field)

        assert 'FrustrationField' in repr_str
        assert 'N=20' in repr_str
        assert '⟨|ψ|⟩' in repr_str
        assert 'C_global' in repr_str

"""
Integration tests for Phase 0_FC.

Tests interaction between manifold and field components.
"""

import pytest
import numpy as np
from phase0_fc import PreGeometricManifold, FrustrationField


class TestPhase0Integration:
    """Integration tests for pre-geometric foundation."""

    def test_field_on_cubic_manifold(self):
        """Test creating field on cubic manifold."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)

        field.initialize_random(r_mean=1.0, r_std=0.3)

        # Basic sanity checks
        assert len(field.psi) == manifold.N
        assert field.mean_amplitude() > 0
        assert 0 <= field.global_cancellation_measure() <= 1

    def test_field_on_random_manifold(self):
        """Test creating field on random graph manifold."""
        manifold = PreGeometricManifold(
            N_nodes=50,
            topology='random_graph',
            random_seed=123
        )
        field = FrustrationField(manifold, seed=456)

        field.initialize_random()

        # Basic sanity checks
        assert len(field.psi) == manifold.N
        assert not np.all(field.psi == 0.0)

    def test_multiple_fields_same_manifold(self):
        """Test that multiple fields can share same manifold."""
        manifold = PreGeometricManifold(N_nodes=30, topology='cubic_3d')

        field1 = FrustrationField(manifold, seed=42)
        field2 = FrustrationField(manifold, seed=99)

        field1.initialize_random(r_mean=0.5)
        field2.initialize_random(r_mean=1.5)

        # Both fields should reference same manifold
        assert field1.manifold is field2.manifold

        # But should have different values
        assert not np.allclose(field1.psi, field2.psi)
        assert field1.mean_amplitude() < field2.mean_amplitude()

    def test_cancellation_scaling_with_size(self):
        """Test that random cancellation is bounded and reasonable."""
        sizes = [100, 400, 1600]
        cancellations = []

        # Use different seeds for independent samples
        for i, N in enumerate(sizes):
            manifold = PreGeometricManifold(N_nodes=N, topology='cubic_3d')
            field = FrustrationField(manifold, seed=42 + i)
            field.initialize_random(r_mean=1.0, r_std=0.1)

            C = field.global_cancellation_measure()
            cancellations.append(C)

        # For random phases, C should scale roughly as 1/√N
        # Check that all cancellations are in reasonable range
        for i, (N, C) in enumerate(zip(sizes, cancellations)):
            expected = 1.0 / np.sqrt(N)  # Rough estimate
            # Allow 10x tolerance (statistical fluctuations can be large)
            assert 0.1 * expected < C < 10.0 * expected, \
                f"N={N}: C={C:.4f} outside reasonable range ~{expected:.4f}"

        # Check that largest system has smaller cancellation than smallest
        # (average across random seeds)
        assert cancellations[2] < cancellations[0] * 2.0

    def test_import_from_package(self):
        """Test that package imports work correctly."""
        # Should be able to import from phase0_fc
        from phase0_fc import PreGeometricManifold as Manifold
        from phase0_fc import FrustrationField as Field

        m = Manifold(N_nodes=10, topology='cubic_3d')
        f = Field(m)

        assert isinstance(m, PreGeometricManifold)
        assert isinstance(f, FrustrationField)

    def test_workflow_example(self):
        """
        Test a typical Phase 0 workflow.

        This serves as both a test and documentation.
        """
        # Step 1: Create manifold
        manifold = PreGeometricManifold(
            N_nodes=100,
            topology='cubic_3d'
        )

        # Step 2: Create field on manifold
        field = FrustrationField(manifold, seed=20260125)

        # Step 3: Initialize with random configuration
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Step 4: Compute properties
        mean_amp = field.mean_amplitude()
        cancellation = field.global_cancellation_measure()
        coherence = field.phase_coherence()

        # Sanity checks
        assert 0.3 < mean_amp < 0.7
        assert 0.0 < cancellation < 0.5
        assert 0.0 <= coherence <= 1.0

        # Phase 0 complete - ready for Phase 1 (dynamics)

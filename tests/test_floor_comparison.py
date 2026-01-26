"""
Tests for floor comparison and scaling analysis.

Tests:
- Comparison with imposed floor (ε=0.01)
- Order-of-magnitude consistency
- Scaling analysis
"""

import pytest
import numpy as np
import pandas as pd
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics
from phase3_fc import FloorDerivation


class TestFloorComparison:
    """Test floor comparison and consistency."""

    def test_compare_floors_structure(self):
        """Test that compare_floors returns correct structure."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        derivation = FloorDerivation(manifold)
        comparison = derivation.compare_floors(epsilon_imposed=0.01, field=field)

        # Should be a DataFrame
        assert isinstance(comparison, pd.DataFrame)

        # Should have 4 rows (holographic, information, topological, imposed)
        assert len(comparison) == 4

        # Should have required columns
        assert 'Method' in comparison.columns
        assert 'Floor (ε)' in comparison.columns
        assert 'Ratio to Imposed' in comparison.columns

        # Check methods are present
        methods = set(comparison['Method'].values)
        assert 'Holographic' in methods
        assert 'Information' in methods
        assert 'Topological' in methods
        assert 'Imposed (Phase 1)' in methods

    def test_imposed_floor_ratio_is_one(self):
        """Test that imposed floor has ratio = 1.0."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        derivation = FloorDerivation(manifold)

        comparison = derivation.compare_floors(epsilon_imposed=0.01)

        # Find imposed row
        imposed_row = comparison[comparison['Method'] == 'Imposed (Phase 1)']
        assert len(imposed_row) == 1

        # Ratio should be exactly 1.0
        ratio = imposed_row['Ratio to Imposed'].values[0]
        assert ratio == 1.0

        # Floor should match imposed value
        floor = imposed_row['Floor (ε)'].values[0]
        assert floor == 0.01

    def test_order_of_magnitude_consistency(self):
        """
        Test that derived floors are within order of magnitude of imposed floor.

        Contract acceptance criterion: 0.1 < ratio < 10
        """
        manifold = PreGeometricManifold(N_nodes=125, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        derivation = FloorDerivation(manifold)
        epsilon_imposed = 0.01

        comparison = derivation.compare_floors(epsilon_imposed=epsilon_imposed, field=field)

        # Get derived methods (exclude imposed)
        derived = comparison[comparison['Method'] != 'Imposed (Phase 1)']

        # All ratios should be within factor of 10 (acceptance criterion)
        for _, row in derived.iterrows():
            ratio = row['Ratio to Imposed']
            assert 0.1 < ratio < 10.0, \
                f"{row['Method']}: ratio {ratio:.2f} outside acceptable range [0.1, 10.0]"

    def test_all_derived_floors_positive(self):
        """Test that all derived floors are positive."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        derivation = FloorDerivation(manifold)
        comparison = derivation.compare_floors(epsilon_imposed=0.01, field=field)

        # All floors should be positive
        for _, row in comparison.iterrows():
            floor = row['Floor (ε)']
            assert floor > 0, f"{row['Method']}: floor {floor} not positive"

    def test_scaling_analysis(self):
        """Test scaling analysis across different system sizes."""
        N_values = [27, 64, 125]
        derivation_dummy = FloorDerivation(
            PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        )

        scaling_data = derivation_dummy.scaling_analysis(N_values, topology='cubic_3d')

        # Should be a DataFrame
        assert isinstance(scaling_data, pd.DataFrame)

        # Should have correct number of rows
        assert len(scaling_data) == len(N_values)

        # Should have required columns
        assert 'N' in scaling_data.columns
        assert 'ε_holographic' in scaling_data.columns
        assert 'ε_information' in scaling_data.columns
        assert 'ε_topological' in scaling_data.columns

        # All floors should be positive
        assert np.all(scaling_data['ε_holographic'] > 0)
        assert np.all(scaling_data['ε_information'] > 0)
        assert np.all(scaling_data['ε_topological'] > 0)

        # Floors should generally decrease with N (scaling)
        # (Holographic and topological scale as ~1/sqrt(N))
        holo_floors = scaling_data['ε_holographic'].values
        assert holo_floors[1] < holo_floors[0]  # N=64 < N=27
        assert holo_floors[2] < holo_floors[1]  # N=125 < N=64

    def test_scaling_power_law(self):
        """Test that floors approximately follow power-law scaling."""
        N_values = [27, 64, 125, 216]
        derivation_dummy = FloorDerivation(
            PreGeometricManifold(N_nodes=27, topology='cubic_3d')
        )

        scaling_data = derivation_dummy.scaling_analysis(N_values, topology='cubic_3d')

        # Holographic floor should scale as ~ N^(-1/2)
        # Check that log(ε) ~ -0.5 * log(N)
        log_N = np.log(scaling_data['N'].values)
        log_eps_holo = np.log(scaling_data['ε_holographic'].values)

        # Linear fit in log-log space
        coeffs = np.polyfit(log_N, log_eps_holo, deg=1)
        exponent = coeffs[0]

        # Exponent should be approximately -0.5
        assert -0.7 < exponent < -0.3, \
            f"Holographic floor exponent {exponent:.2f} not close to -0.5"

    def test_compare_floors_with_evolved_field(self):
        """Test floor comparison with evolved (non-trivial) field."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Evolve field
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05
        )
        dynamics.evolve_trajectory(n_steps=50, dt=0.01)

        # Derive floors from evolved field
        derivation = FloorDerivation(manifold)
        comparison = derivation.compare_floors(epsilon_imposed=0.01, field=field)

        # Should work with evolved field
        assert len(comparison) == 4
        assert np.all(comparison['Floor (ε)'] > 0)

    def test_contract_acceptance_criteria(self):
        """
        Test Phase 3 contract acceptance criteria.

        Criteria:
        - All derived floors positive
        - All derived floors bounded: 1e-6 < ε < 1e0
        - Order-of-magnitude consistency: 0.1 < ratio < 10
        - Reproducible
        """
        manifold = PreGeometricManifold(N_nodes=125, topology='cubic_3d', random_seed=20260126)
        field = FrustrationField(manifold, seed=20260126)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        # Optionally evolve field
        dynamics = FrustratedDynamics(
            field=field,
            gamma=0.1,
            omega=1.0,
            epsilon=0.01,
            drive_amplitude=0.05,
            drive_seed=123
        )
        dynamics.evolve_trajectory(n_steps=50, dt=0.01)

        derivation = FloorDerivation(manifold)
        epsilon_imposed = 0.01

        # Derive all floors
        eps_holo, diag_holo = derivation.holographic_floor()
        eps_info, diag_info = derivation.information_floor(field=field)
        eps_topo, diag_topo = derivation.topological_floor()

        # Criterion 1: All positive
        assert eps_holo > 0
        assert eps_info > 0
        assert eps_topo > 0

        # Criterion 2: All bounded
        assert 1e-6 < eps_holo < 1.0
        assert 1e-6 < eps_info < 10.0
        assert 1e-6 < eps_topo < 1.0

        # Criterion 3: Order-of-magnitude consistency
        ratio_holo = eps_holo / epsilon_imposed
        ratio_info = eps_info / epsilon_imposed
        ratio_topo = eps_topo / epsilon_imposed

        assert 0.1 < ratio_holo < 10.0, \
            f"Holographic ratio {ratio_holo:.2f} outside [0.1, 10]"
        assert 0.1 < ratio_info < 10.0, \
            f"Information ratio {ratio_info:.2f} outside [0.1, 10]"
        assert 0.1 < ratio_topo < 10.0, \
            f"Topological ratio {ratio_topo:.2f} outside [0.1, 10]"

        # Criterion 4: Reproducibility
        eps_holo2, _ = derivation.holographic_floor()
        assert eps_holo == eps_holo2

        # All acceptance criteria met

    def test_comparison_table_values(self):
        """Test that comparison table has reasonable values."""
        manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d')
        field = FrustrationField(manifold, seed=42)
        field.initialize_random(r_mean=0.5, r_std=0.2)

        derivation = FloorDerivation(manifold)
        comparison = derivation.compare_floors(epsilon_imposed=0.01, field=field)

        # All floors should be in reasonable range
        for _, row in comparison.iterrows():
            floor = row['Floor (ε)']
            assert floor > 0
            assert floor < 1.0  # Floors should be << 1

        # All ratios should be positive
        for _, row in comparison.iterrows():
            ratio = row['Ratio to Imposed']
            assert ratio > 0

    def test_floor_derivation_without_field(self):
        """Test that floor derivation works without field (theoretical bounds)."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        derivation = FloorDerivation(manifold)

        # Should work without field (uses theoretical bounds)
        comparison = derivation.compare_floors(epsilon_imposed=0.01, field=None)

        assert len(comparison) == 4
        assert np.all(comparison['Floor (ε)'] > 0)

    def test_different_imposed_values(self):
        """Test comparison with different imposed floor values."""
        manifold = PreGeometricManifold(N_nodes=64, topology='cubic_3d')
        derivation = FloorDerivation(manifold)

        imposed_values = [0.001, 0.01, 0.1]

        for eps_imposed in imposed_values:
            comparison = derivation.compare_floors(epsilon_imposed=eps_imposed)

            # Imposed row should have correct value
            imposed_row = comparison[comparison['Method'] == 'Imposed (Phase 1)']
            assert imposed_row['Floor (ε)'].values[0] == eps_imposed
            assert imposed_row['Ratio to Imposed'].values[0] == 1.0

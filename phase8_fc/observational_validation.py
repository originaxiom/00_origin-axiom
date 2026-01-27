"""
Phase 8_FC: Observational Validation

Compare frustrated cancellation predictions with cosmological observations:
- DESI w(z) measurements
- Planck H₀ measurements
- Hubble tension
- Distance modulus
"""

import numpy as np
from typing import Dict, Tuple, Optional
from scipy.interpolate import interp1d
from scipy.optimize import minimize


class ObservationalValidator:
    """
    Compare framework predictions with observational data.

    Tracks w(z), H(z), d_L(z) and compares with:
    - DESI BAO measurements
    - Planck CMB constraints
    - SNe Ia distances
    """

    def __init__(self):
        """Initialize validator with observational data."""
        # DESI-like w(z) measurements (simplified)
        # Real DESI: w(z) = w0 + wa*z/(1+z)
        # Best fit: w0 = -0.827, wa = -0.75
        self.desi_z = np.array([0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5])
        self.desi_w = np.array([-0.82, -0.85, -0.88, -0.90, -0.92, -0.94, -0.95])
        self.desi_w_err = np.array([0.06, 0.07, 0.07, 0.08, 0.09, 0.10, 0.11])

        # Planck H0 (km/s/Mpc)
        self.H0_planck = 67.4
        self.H0_planck_err = 0.5

        # Local H0 (SH0ES, km/s/Mpc)
        self.H0_local = 73.04
        self.H0_local_err = 1.04

        # Age of universe (Gyr)
        self.age_obs = 13.80
        self.age_obs_err = 0.02

    def track_w_vs_z(self,
                     a_history: np.ndarray,
                     w_history: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert w(τ) and a(τ) to w(z).

        Parameters
        ----------
        a_history : np.ndarray
            Scale factor history (normalized, a(0)=1)
        w_history : np.ndarray
            Equation of state history w(τ)

        Returns
        -------
        z_pred : np.ndarray
            Redshift array
        w_pred : np.ndarray
            Equation of state at each z
        """
        # Compute redshift from scale factor
        # z = a_0/a - 1, where a_0 = 1 (present)
        z_history = (1.0 / a_history) - 1.0

        # Sort by z (since a decreases, z increases)
        sort_idx = np.argsort(z_history)
        z_sorted = z_history[sort_idx]
        w_sorted = w_history[sort_idx]

        # Remove any negative z (future, if a > 1)
        valid = z_sorted >= 0
        z_pred = z_sorted[valid]
        w_pred = w_sorted[valid]

        return z_pred, w_pred

    def compare_with_DESI(self,
                          z_pred: np.ndarray,
                          w_pred: np.ndarray) -> Dict:
        """
        Compare predicted w(z) with DESI measurements.

        Parameters
        ----------
        z_pred : np.ndarray
            Predicted redshift array
        w_pred : np.ndarray
            Predicted w at each z

        Returns
        -------
        comparison : dict
            'chi2': χ² value
            'dof': degrees of freedom
            'chi2_reduced': χ²/dof
            'w_at_desi_z': w_pred interpolated to DESI z points
            'residuals': (w_pred - w_obs)/σ
        """
        # Interpolate our prediction to DESI z points
        if len(z_pred) < 2:
            return {
                'chi2': np.inf,
                'dof': len(self.desi_z),
                'chi2_reduced': np.inf,
                'w_at_desi_z': np.full(len(self.desi_z), np.nan),
                'residuals': np.full(len(self.desi_z), np.nan)
            }

        # Create interpolator (extrapolate if needed)
        try:
            w_interp = interp1d(z_pred, w_pred,
                               kind='linear',
                               bounds_error=False,
                               fill_value='extrapolate')

            w_at_desi_z = w_interp(self.desi_z)

            # Compute residuals and χ²
            residuals = (w_at_desi_z - self.desi_w) / self.desi_w_err
            chi2 = np.sum(residuals**2)
            dof = len(self.desi_z)
            chi2_reduced = chi2 / dof

            return {
                'chi2': chi2,
                'dof': dof,
                'chi2_reduced': chi2_reduced,
                'w_at_desi_z': w_at_desi_z,
                'residuals': residuals
            }
        except Exception as e:
            return {
                'chi2': np.inf,
                'dof': len(self.desi_z),
                'chi2_reduced': np.inf,
                'w_at_desi_z': np.full(len(self.desi_z), np.nan),
                'residuals': np.full(len(self.desi_z), np.nan),
                'error': str(e)
            }

    def fit_w0_wa(self,
                  z_pred: np.ndarray,
                  w_pred: np.ndarray) -> Dict:
        """
        Fit w(z) = w0 + wa*z/(1+z) form (CPL parameterization).

        Parameters
        ----------
        z_pred : np.ndarray
            Predicted redshift
        w_pred : np.ndarray
            Predicted w(z)

        Returns
        -------
        fit_params : dict
            'w0': constant term
            'wa': evolution term
            'chi2': fit quality
        """
        def model(z, w0, wa):
            return w0 + wa * z / (1 + z)

        def residuals(params):
            w0, wa = params
            w_model = model(z_pred, w0, wa)
            return np.sum((w_pred - w_model)**2)

        # Initial guess
        w0_guess = np.mean(w_pred[z_pred < 0.5]) if any(z_pred < 0.5) else -1.0
        wa_guess = 0.0

        try:
            result = minimize(residuals, [w0_guess, wa_guess], method='Nelder-Mead')
            w0_fit, wa_fit = result.x
            chi2_fit = result.fun

            return {
                'w0': w0_fit,
                'wa': wa_fit,
                'chi2': chi2_fit,
                'success': result.success
            }
        except:
            return {
                'w0': np.nan,
                'wa': np.nan,
                'chi2': np.inf,
                'success': False
            }

    def assess_viability(self, comparison: Dict) -> str:
        """
        Assess if framework is viable based on χ².

        Returns 'viable', 'marginal', or 'ruled_out'.
        """
        chi2_red = comparison['chi2_reduced']

        if chi2_red < 1.5:
            return 'viable'  # Good fit
        elif chi2_red < 3.0:
            return 'marginal'  # Acceptable fit
        else:
            return 'ruled_out'  # Poor fit

    def compute_hubble_ratio(self,
                             H_pred: float,
                             comparison_type: str = 'planck') -> Dict:
        """
        Compare predicted H₀ with observations.

        NOTE: This requires unit conversion from code units to km/s/Mpc,
        which is nontrivial. For now, we report ratio.

        Parameters
        ----------
        H_pred : float
            Predicted H₀ in code units
        comparison_type : str
            'planck' or 'local'

        Returns
        -------
        comparison : dict
            Hubble comparison metrics
        """
        if comparison_type == 'planck':
            H_obs = self.H0_planck
            H_err = self.H0_planck_err
        else:
            H_obs = self.H0_local
            H_err = self.H0_local_err

        # Can't directly compare without units
        # Report H_pred in code units for reference
        return {
            'H_pred_code_units': H_pred,
            'H_obs_km_s_Mpc': H_obs,
            'H_err_km_s_Mpc': H_err,
            'note': 'Unit conversion required for direct comparison'
        }

    def generate_report(self,
                        comparison_desi: Dict,
                        fit_params: Dict,
                        assessment: str) -> str:
        """
        Generate human-readable report.

        Returns
        -------
        report : str
            Formatted assessment
        """
        report = []
        report.append("=" * 70)
        report.append("OBSERVATIONAL VALIDATION REPORT")
        report.append("=" * 70)

        report.append("\n1. DESI Comparison")
        report.append(f"   χ² = {comparison_desi['chi2']:.2f}")
        report.append(f"   d.o.f. = {comparison_desi['dof']}")
        report.append(f"   χ²/d.o.f. = {comparison_desi['chi2_reduced']:.2f}")

        if comparison_desi['chi2_reduced'] < 1.5:
            report.append("   → GOOD FIT ✓")
        elif comparison_desi['chi2_reduced'] < 3.0:
            report.append("   → ACCEPTABLE FIT")
        else:
            report.append("   → POOR FIT ✗")

        report.append("\n2. w(z) Parameterization")
        if fit_params['success']:
            report.append(f"   w₀ = {fit_params['w0']:.3f}")
            report.append(f"   wₐ = {fit_params['wa']:.3f}")
            report.append(f"   (DESI: w₀ = -0.827, wₐ = -0.75)")
        else:
            report.append("   Fit failed")

        report.append(f"\n3. Overall Assessment: {assessment.upper()}")

        if assessment == 'viable':
            report.append("   ✓ Framework predictions match observations")
            report.append("   ✓ Competitive with ΛCDM")
        elif assessment == 'marginal':
            report.append("   ~ Framework marginally consistent")
            report.append("   ~ Needs refinement but not ruled out")
        else:
            report.append("   ✗ Framework ruled out by observations")
            report.append("   ✗ Predictions contradict data")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

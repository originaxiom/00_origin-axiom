# Phase 9_FC Contract: Refinement & Extension

**Status:** ACTIVE
**Version:** v1.0
**Date:** 2026-01-27

---

## Purpose

Phase 9 addresses the limitations discovered in Phase 8 observational validation. After achieving marginal viability (χ²/dof = 1.52), we now refine the framework to:

1. **Extend redshift coverage** - Currently z_max ≈ 0.12, need z ∈ [0, 2]
2. **Establish time mapping** - Connect emergent τ to cosmic time t
3. **Optimize parameters** - Explore (V, γ) jointly, not just V
4. **Add observational tests** - Distance modulus for SNe Ia

**Goal:** Improve χ²/dof from 1.52 to <1.3 and achieve full DESI redshift coverage.

**Critical question:** Can systematic parameter optimization and extended evolution reduce the 2σ tension at low redshifts?

---

## Motivation

### Phase 8 Limitations

1. **Limited z range:** Only reached z_max ≈ 0.12 in 200-step evolution
   - DESI data spans z ∈ [0.3, 1.5]
   - Need interpolation to compare → introduces uncertainty

2. **Low-z tension:** Predictions 2σ too negative at z < 0.5
   - Systematic offset suggests parameter mismatch
   - May improve with better (V, γ) fit

3. **1D parameter space:** Only V explored, γ/ω/K at defaults
   - May miss better-fit configurations
   - 2D scan could find global minimum

4. **No SNe Ia test:** Only DESI BAO so far
   - Distance modulus provides independent validation
   - Pantheon+ has ~1500 supernovae

5. **τ-t mapping unclear:** Can't compare H₀ quantitatively
   - Need this for Hubble tension test
   - Requires fundamental timescale identification

### Expected Improvements

With Phase 9 refinements:
- χ²/dof: 1.52 → ~1.2-1.3 (viable → strongly viable)
- Redshift coverage: z_max 0.12 → 2.0 (full DESI range)
- Parameter constraints: V-only → (V, γ) optimization
- Observational tests: DESI only → DESI + SNe Ia
- H₀ readiness: τ units → km/s/Mpc conversion

---

## Scope

### In Scope

#### 1. Extended Redshift Range

**Current:** 200 evolution steps → z_max ≈ 0.12
**Target:** Reach z ∈ [0, 2] to cover full DESI/SNe range

**Implementation:**
- Increase evolution steps: 200 → 2000
- Monitor numerical stability at late times
- Verify a(τ) decay is smooth and physical
- Check that w(z) remains well-defined

**Success metric:** z_max ≥ 1.5 with stable evolution

#### 2. τ-t Time Mapping

**Goal:** Establish correspondence between emergent time τ and cosmic time t

**Approaches to test:**

**A. Match H₀:**
- Normalize H(z=0) to observed H₀ = 67-73 km/s/Mpc
- Establishes conversion factor: τ_code ↔ t_Gyr
- Simple but requires choosing Planck vs local

**B. Match age:**
- Compute t₀ = ∫dτ/a from evolution
- Compare with observed 13.8 Gyr
- More fundamental than H₀ matching

**C. Drive scale:**
- Identify K as setting timescale
- τ ~ 1/√K in code units
- Connect to fundamental physics scale

**D. Floor scale:**
- ε sets minimum energy ~ vacuum energy
- ε^(1/4) ~ energy scale
- May connect to Λ^(1/4) ~ 2.3 meV

**Deliverable:** τ → t conversion formula with justification

#### 3. 2D Parameter Scan (V, γ)

**Current:** V ∈ [0, 50] with γ=0.1 fixed
**Target:** Explore (V, γ) jointly to find global χ² minimum

**Grid:**
```
V ∈ [0, 50], 10 points (0, 2.5, 5, 10, 15, 20, 30, 40, 50)
γ ∈ [0.01, 1.0], 6 points (0.01, 0.05, 0.1, 0.3, 0.5, 1.0)
Total: 60 configurations
```

**For each (V, γ):**
- Evolve cosmology 2000 steps
- Compute w(z) over full range
- Calculate χ²_DESI
- Record w₀, wₐ parameters

**Output:**
- χ²(V, γ) landscape/heatmap
- Best-fit (V_opt, γ_opt)
- Comparison with Phase 8 V=5.0, γ=0.1

**Success metric:** χ²/dof < 1.3 for optimal configuration

#### 4. Distance Modulus Calculation

**Goal:** Compare luminosity distance d_L(z) with SNe Ia

**Implementation:**
```python
# Compute comoving distance
d_C(z) = ∫₀^z dz'/H(z')

# Luminosity distance
d_L(z) = (1+z) × d_C(z)

# Distance modulus
μ(z) = 5 log₁₀(d_L/10pc) + 25
```

**Data:** Pantheon+ SNe Ia sample
- ~1500 supernovae
- z ∈ [0.001, 2.3]
- Standardized distance moduli

**Comparison:**
- Compute χ²_SNe = Σ[(μ_pred - μ_obs)/σ_μ]²
- Combined fit: χ²_total = χ²_DESI + χ²_SNe
- Assess overall viability

**Success metric:** χ²_SNe/dof < 2.0 (loose constraint)

#### 5. Improved Observational Validator

**Extend `phase8_fc/observational_validation.py`:**
- Add `compute_distance_modulus()` method
- Add `compare_with_SNe()` method
- Add `combined_chi2()` for joint fits
- Support for longer evolution (2000 steps)

**New methods:**
```python
def compute_redshift_array(self, a_history):
    """Convert scale factor to redshift array."""
    z = a_history[0] / a_history - 1
    return z

def compute_distance_modulus(self, z, H_z):
    """Compute μ(z) from H(z)."""
    # Integrate to get d_C, then d_L, then μ
    pass

def compare_with_SNe(self, z, mu_pred):
    """Compare with Pantheon+ sample."""
    # Load SNe data, compute χ²
    pass
```

### Out of Scope

**Not in Phase 9:**
- Matter sector (ρ_matter) → Phase 11
- Growth rate f(z) → Phase 12
- CMB power spectrum → Phase 16
- Quantum formulation → Phase 14+
- 4D parameter optimization (V, γ, ω, K) → Phase 10
- Time-varying potential V(τ) → Phase 13
- Spatial gradient deep dive → Phase 10

**Non-Claims:**
- We do NOT claim this solves fine-tuning (yet)
- We do NOT claim better than ΛCDM (yet)
- We do NOT claim to explain H₀ tension (testing only)
- We do NOT claim completeness (missing matter)

---

## Acceptance Criteria

Phase 9 is ACCEPTED if:

### AC1: Extended Redshift Range
- ✓ Evolution reaches z_max ≥ 1.5
- ✓ Scale factor a(τ) decays smoothly
- ✓ w(z) well-defined over full range
- ✓ Numerical stability maintained
- ✓ No unphysical divergences

### AC2: τ-t Time Mapping Established
- ✓ Conversion formula τ → t documented
- ✓ Justification for chosen approach
- ✓ H(z=0) value extracted in km/s/Mpc
- ✓ Age t₀ computed in Gyr
- ✓ Comparison with observations (H₀ ≈ 70, t₀ ≈ 13.8 Gyr)

### AC3: 2D Parameter Scan Complete
- ✓ (V, γ) grid explored (≥50 points)
- ✓ χ²(V, γ) landscape computed
- ✓ Global minimum identified
- ✓ Best fit improves over Phase 8
- ✓ Results documented with visualization

### AC4: Distance Modulus Implemented
- ✓ d_L(z) computation working
- ✓ μ(z) calculation correct
- ✓ SNe Ia comparison completed
- ✓ χ²_SNe calculated
- ✓ Combined χ²_total assessed

### AC5: Improved χ² Fit
- ✓ χ²_DESI/dof < 1.3 achieved (stretch goal)
- ✓ OR χ²_DESI/dof < 1.4 AND χ²_total/dof < 1.5
- ✓ Better than Phase 8 baseline (1.52)
- ✓ Tension at low-z reduced

### AC6: Documentation & Assessment
- ✓ RESULTS.md created with findings
- ✓ Comparison tables (Phase 8 vs Phase 9)
- ✓ Honest assessment of improvements
- ✓ Remaining limitations documented
- ✓ Recommendations for Phase 10

---

## Implementation Plan

### Task 1: Extend Evolution (2-3 hours)

**Modify `phase6_fc/cosmology.py`:**
```python
def evolve_cosmology(self, n_steps=2000, dtau=0.001, ...):
    # Increase default n_steps from 200 to 2000
    # Monitor stability
    # Return longer a_history, w_history
```

**Test:**
- Run with V=5.0, γ=0.1
- Verify z_max ≥ 1.5
- Check w(z) behavior

### Task 2: τ-t Mapping (3-4 hours)

**Create `phase9_fc/time_mapping.py`:**
```python
class TimescaleMapper:
    def __init__(self, H0_target=70.0):
        self.H0_target = H0_target  # km/s/Mpc

    def calibrate_from_H0(self, H_tau_at_z0):
        """Match H(z=0) to H₀."""
        # H_tau has code units
        # H₀ has km/s/Mpc
        # Find conversion factor
        self.tau_to_Gyr = ...

    def calibrate_from_age(self, tau_total, a_history):
        """Match ∫dτ/a to t₀ = 13.8 Gyr."""
        t0_code = np.trapz(1.0/a_history, dx=dtau)
        self.tau_to_Gyr = 13.8 / t0_code

    def convert_to_cosmic_time(self, tau_array):
        """Convert τ → t in Gyr."""
        return tau_array * self.tau_to_Gyr
```

**Test both approaches, document which works better.**

### Task 3: 2D Parameter Scan (4-5 hours)

**Create `experiments/phase9_parameter_scan.py`:**
```python
V_grid = [0, 2.5, 5, 10, 15, 20, 30, 40, 50]
gamma_grid = [0.01, 0.05, 0.1, 0.3, 0.5, 1.0]

results = []
for V in V_grid:
    for gamma in gamma_grid:
        # Evolve cosmology
        # Compute χ²
        # Store results
        results.append({
            'V': V, 'gamma': gamma,
            'chi2': chi2, 'chi2_reduced': chi2/dof,
            'w0': w0, 'wa': wa
        })

# Find best fit
best = min(results, key=lambda x: x['chi2_reduced'])
```

**Output:** CSV table + optional heatmap visualization

### Task 4: Distance Modulus (3-4 hours)

**Extend `phase8_fc/observational_validation.py`:**
```python
def compute_distance_modulus(self, z_array, H_z_array):
    """Compute μ(z) from H(z)."""
    # Numerical integration of 1/H(z)
    d_C = cumulative_trapezoid(1.0/H_z_array, z_array, initial=0)
    d_L = (1 + z_array) * d_C

    # Distance modulus in Mpc
    mu = 5 * np.log10(d_L * 1e6 / 10) + 25
    return mu

def load_SNe_data(self):
    """Load Pantheon+ sample (simplified)."""
    # For Phase 9, use representative subset
    # Full catalog is ~1500 SNe
    self.sne_z = [...]
    self.sne_mu = [...]
    self.sne_mu_err = [...]
```

**Test with computed H(z) from Phase 8.**

### Task 5: Acceptance Test (2 hours)

**Create `experiments/phase9_acceptance_test.py`:**
- Run extended evolution (2000 steps)
- Apply τ-t mapping
- Execute 2D parameter scan
- Compute distance moduli
- Compare all metrics

### Task 6: Documentation (2 hours)

**Create `phase9_fc/RESULTS.md`:**
- Comparison tables (Phase 8 vs 9)
- χ² improvements
- Best-fit parameters
- τ-t mapping justification
- SNe Ia results
- Remaining tensions
- Recommendations for Phase 10

---

## Test Strategy

### Unit Tests

**Add to `tests/test_phase9.py`:**
- `test_extended_evolution_stability()` - 2000 steps no divergence
- `test_time_mapping_H0()` - H₀ extraction correct units
- `test_time_mapping_age()` - t₀ calculation correct
- `test_distance_modulus()` - μ(z) formula correct
- `test_parameter_scan()` - Grid search completes

### Integration Tests

**Add to `tests/test_integration_phase9.py`:**
- Full pipeline Phase 0-9
- Extended evolution → mapping → comparison
- Verify χ² improves over Phase 8

### Acceptance Test

**`experiments/phase9_acceptance_test.py`:**
- Comprehensive validation of all AC1-AC6
- Quantitative metrics vs Phase 8
- Pass/fail assessment

---

## Success Metrics

### Tier 1: Minimal Success
- z_max ≥ 1.0 (not full 2.0 but better than 0.12) ✓
- τ-t mapping established (any method) ✓
- 2D scan shows improvement exists ✓
- Distance modulus computed ✓
- χ²/dof ≤ 1.52 (no worse than Phase 8) ✓

**Verdict:** Phase 9 provides incremental improvement

### Tier 2: Expected Success
- z_max ≥ 1.5 ✓
- τ-t mapping with H₀ ~ 70 km/s/Mpc ✓
- χ²/dof < 1.4 ✓
- Best fit better than Phase 8 baseline ✓
- SNe Ia χ²/dof < 2.0 ✓

**Verdict:** Phase 9 achieves refinement goals

### Tier 3: Stretch Goals
- z_max ≥ 2.0 (full DESI) ✓
- χ²/dof < 1.3 (strongly viable) ✓
- Low-z tension reduced to <1.5σ ✓
- H₀ prediction within 10% of observations ✓
- Combined χ²_total < 1.5 ✓

**Verdict:** Framework approaching competitiveness with ΛCDM

---

## Expected Challenges

### 1. Numerical Stability at Long Evolution
**Problem:** 2000 steps may show instabilities
**Mitigation:**
- Adaptive step size
- Monitor energy conservation
- Check floor violations

### 2. τ-t Mapping Ambiguity
**Problem:** Multiple methods give different results
**Mitigation:**
- Test all approaches
- Document which is most physical
- Report range of values

### 3. Computational Cost
**Problem:** 60-point 2D scan × 2000 steps = ~120,000 steps total
**Mitigation:**
- Run in parallel if possible
- Use coarser grid first, refine around minimum
- ~1-2 hours runtime expected

### 4. SNe Ia Data Access
**Problem:** Full Pantheon+ catalog large
**Mitigation:**
- Use representative subset (100-200 SNe)
- Or use binned data
- Focus on z < 2 where FC framework applies

### 5. Parameter Degeneracy
**Problem:** Multiple (V, γ) may give similar χ²
**Mitigation:**
- Plot χ²(V, γ) landscape
- Identify degeneracy directions
- Report viable region, not just minimum

---

## Risk Assessment

### Risk 1: χ² Doesn't Improve
**Probability:** 30%
**Impact:** Phase 9 confirms χ²/dof ~ 1.5 is fundamental limit
**Mitigation:** Still valuable to know limit, document why

### Risk 2: Extended z Shows Worse Fit
**Probability:** 20%
**Impact:** Tensions increase at z > 0.5
**Mitigation:** Identify valid regime (z < 0.5 only)

### Risk 3: τ-t Mapping Gives Wrong H₀
**Probability:** 40%
**Impact:** H₀ prediction is 50 or 100 km/s/Mpc (way off)
**Mitigation:** Document discrepancy, identify missing physics

### Risk 4: 2D Scan Shows Flat Landscape
**Probability:** 25%
**Impact:** All (V, γ) give similar χ²
**Mitigation:** Suggests framework insensitive to γ, focus on V

### Risk 5: Computational Issues
**Probability:** 15%
**Impact:** 2000-step evolution diverges or hangs
**Mitigation:** Reduce to 1000 steps, still better than 200

---

## Deliverables

### Code
1. `phase9_fc/time_mapping.py` - τ → t conversion class
2. `phase9_fc/__init__.py` - Module exports
3. Updated `phase8_fc/observational_validation.py` - Distance modulus
4. `experiments/phase9_parameter_scan.py` - 2D optimization
5. `experiments/phase9_acceptance_test.py` - Full validation

### Documentation
1. `phase9_fc/CONTRACT.md` - This file
2. `phase9_fc/RESULTS.md` - Findings and comparisons
3. Updated `README.md` - Phase 9 status
4. Updated `STATUS_SNAPSHOT.md` - Current state

### Tests
1. `tests/test_phase9.py` - Unit tests
2. `tests/test_integration_phase9.py` - Integration tests

### Outputs
1. `outputs/phase9_parameter_scan.csv` - Full 2D grid results
2. `outputs/phase9_best_fit.txt` - Optimal parameters
3. `outputs/phase9_test.log` - Acceptance test output

---

## Timeline

**Total estimated time:** 15-20 hours

- Task 1 (Extend evolution): 2-3 hours
- Task 2 (τ-t mapping): 3-4 hours
- Task 3 (2D scan): 4-5 hours
- Task 4 (Distance modulus): 3-4 hours
- Task 5 (Acceptance test): 2 hours
- Task 6 (Documentation): 2 hours

**Wall-clock time:** 3-5 days (with breaks)

---

## Notes

- This phase is **refinement**, not radical new physics
- Focus on squeezing best performance from existing framework
- Even if χ² doesn't improve much, extended range and mapping are valuable
- Negative results (e.g., χ² stuck at 1.5) are informative
- Be honest about what improves and what doesn't
- Document limitations clearly for Phase 10 planning

**Phase 9 success means:** Framework is ready for mechanism investigations (Phase 10) and matter coupling (Phase 11).

---

**Status:** Ready to implement
**Dependencies:** Phase 8 complete ✓
**Next:** Implement extended evolution and time mapping

---

**Contract maintained by:** Claude
**Approved by:** User directive "Update readme and all other relevant documentation to reflect the progress? Then we go for phase 9."
**Date:** 2026-01-27

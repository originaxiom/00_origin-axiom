# Phase 6_FC Contract: Cosmological Observables

**Status:** ACCEPTED
**Version:** v1.0
**Date:** 2026-01-26
**Accepted:** 2026-01-26

---

## Purpose

Phase 6 extracts **cosmological observables** from frustrated cancellation dynamics to test whether the framework describes the actual universe.

- Previous phases: internal self-consistency (floor, time, drive all emerge)
- Now: connect to measurable cosmology (H(t), a(t), w(z))
- Test: do predictions match observations (DESI, Planck, etc.)?

**Goal:** Bridge "frustrated striving" (mathematical abstraction) to "expanding universe" (observable reality).

**Critical question:** Does emergent energy density from striving dynamics yield realistic cosmological evolution, or does the framework produce unphysical behavior?

---

## Scope

### In Scope

1. **Energy density mapping**
   - Global energy: ρ(τ) = ⟨|∂ψ/∂τ|²⟩
   - Spatial average over manifold
   - Track evolution: ρ(τ) as system evolves
   - Units: convert to physical density (if possible)

2. **Hubble parameter extraction**
   - From time evolution: H ~ (1/a)(da/dt)
   - From energy: H² ~ ρ (Friedmann-like relation)
   - Track H(τ) over evolution
   - Compare with emergent time dt

3. **Equation of state**
   - Compute w = P/ρ where P = pressure
   - From energy-momentum: P ~ (1/3)⟨(∂ψ/∂τ)²⟩ (if isotropic)
   - Or: w from dρ/dt + 3H(ρ + P) = 0
   - Track w(τ) or w(z) if redshift definable

4. **Scale factor evolution**
   - Define a(τ) from "expansion" of ψ field
   - Option 1: a ~ ⟨|ψ|⟩ (mean amplitude)
   - Option 2: a ~ correlation length
   - Option 3: a from H via da/dt = Ha
   - Verify consistency

5. **Observational comparison**
   - If w(z) computable → compare with DESI bounds
   - If H(t) computable → compare with Planck/local H₀
   - If acceleration → check when/why occurs
   - Document matches and mismatches

### Out of Scope

**Not in Phase 6:**
- Matter sector (baryons, dark matter) → No particles yet
- Perturbations (δρ/ρ, power spectra) → Homogeneous limit only
- Radiation era → Focus on "dark energy" limit
- Quantum observables → Classical framework
- Full GR field equations → Friedmann analogy only
- Parameter fitting to data → Just check plausibility

### Non-Claims

**We do NOT claim:**
- That this is a complete cosmological model
- That matter can be ignored forever
- That w(z) will match observations precisely
- That H₀ tension is resolved
- That this replaces ΛCDM
- That spatial curvature is handled correctly

---

## Core Objects

### CosmologicalObservables

**Purpose:** Extract H(τ), a(τ), w(τ), ρ(τ) from frustrated dynamics.

**Initialization:**
```python
class CosmologicalObservables:
    def __init__(self,
                 manifold: PreGeometricManifold,
                 dynamics: FrustratedDynamics,
                 time: EmergentTime):
        """
        Initialize cosmological observable extractor.

        Parameters
        ----------
        manifold : PreGeometricManifold
            Topology structure
        dynamics : FrustratedDynamics
            Evolution equations
        time : EmergentTime
            Physical time computation
        """
```

**Key methods:**

1. **compute_energy_density**
   ```python
   def compute_energy_density(self, psi: np.ndarray,
                             psi_dot: np.ndarray) -> float:
       """
       Compute spatial-average energy density.

       ρ(τ) = ⟨|∂ψ/∂τ|²⟩

       Returns
       -------
       rho : float
           Energy density at current state
       """
   ```

2. **compute_hubble_parameter**
   ```python
   def compute_hubble_parameter(self,
                                a: float,
                                da_dt: float) -> float:
       """
       Compute Hubble parameter H = (1/a)(da/dt).

       Parameters
       ----------
       a : float
           Scale factor
       da_dt : float
           Time derivative of scale factor

       Returns
       -------
       H : float
           Hubble parameter
       """
   ```

3. **compute_scale_factor**
   ```python
   def compute_scale_factor(self, psi: np.ndarray,
                           method: str = 'amplitude') -> float:
       """
       Compute scale factor from field state.

       Options:
       - 'amplitude': a ~ ⟨|ψ|⟩
       - 'correlation': a ~ correlation length
       - 'volume': a ~ effective volume

       Returns
       -------
       a : float
           Scale factor (dimensionless, a(τ=0) = 1)
       """
   ```

4. **compute_equation_of_state**
   ```python
   def compute_equation_of_state(self,
                                 rho: float,
                                 pressure: float) -> float:
       """
       Compute w = P/ρ.

       Returns
       -------
       w : float
           Equation of state parameter
       """
   ```

5. **evolve_cosmology**
   ```python
   def evolve_cosmology(self,
                       initial_psi: np.ndarray,
                       n_steps: int,
                       dt: float) -> Dict[str, np.ndarray]:
       """
       Evolve system and track cosmological observables.

       Returns
       -------
       diagnostics : dict
           'tau': parameter time array
           'physical_time': emergent time array
           'rho': energy density history
           'H': Hubble parameter history
           'a': scale factor history
           'w': equation of state history
           'z': redshift (if definable)
       """
   ```

---

## Acceptance Criteria

Phase 6 is ACCEPTED if all of the following are met:

### AC1: Energy density extraction
- ✓ Can compute ρ(τ) = ⟨|∂ψ/∂τ|²⟩
- ✓ ρ remains positive throughout evolution
- ✓ ρ is bounded (no infinities)
- ✓ Reproducible with fixed seeds

### AC2: Hubble parameter extraction
- ✓ Can compute H(τ) from scale factor or Friedmann relation
- ✓ H evolution is smooth (no discontinuities)
- ✓ Sign of H indicates expansion or contraction
- ✓ H remains bounded

### AC3: Equation of state computation
- ✓ Can compute w = P/ρ
- ✓ w values are within physical range [-1.5, +1.5]
- ✓ w evolution tracked over time
- ✓ Sign consistency: w < 0 → acceleration, w > 0 → deceleration

### AC4: Scale factor evolution
- ✓ Can define a(τ) consistently
- ✓ a normalized: a(τ=0) = 1
- ✓ a evolves monotonically (expansion or contraction, not both)
- ✓ da/dt matches H·a within tolerance

### AC5: Integration test
- ✓ Full evolution pipeline: Phase 0 → Phase 5 → Phase 6
- ✓ All observables computed over trajectory
- ✓ Diagnostics include (τ, t, ρ, H, a, w)
- ✓ Results saved to CSV for analysis

### AC6: Observational comparison (qualitative)
- ✓ Document comparison with known cosmology
- ✓ If w ≈ -1 → consistent with Λ
- ✓ If w evolves → compare with DESI bounds w(z)
- ✓ If H₀ estimable → compare with Planck (67 km/s/Mpc) vs local (73 km/s/Mpc)
- ✓ Document any unphysical behavior (w < -1.5, oscillating a, etc.)

---

## Test Strategy

### Unit Tests (test_cosmological_observables.py)

1. **Initialization**
   - CosmologicalObservables initializes correctly
   - All input objects required

2. **Energy density**
   - Positive for non-zero ∂ψ/∂τ
   - Zero for frozen field
   - Scales with amplitude

3. **Hubble parameter**
   - Correct sign for expansion (H > 0) and contraction (H < 0)
   - H = 0 when da/dt = 0
   - Matches analytic cases

4. **Scale factor**
   - a(0) = 1 (normalized)
   - Different methods give consistent results
   - Monotonic evolution

5. **Equation of state**
   - w = P/ρ computed correctly
   - Consistency: w = -1 → constant ρ
   - Consistency: w = 0 → ρ ~ a⁻³

### Integration Tests (test_integration_phase6.py)

1. **Full pipeline**
   - Phase 0-5 → Phase 6
   - All observables extracted
   - No crashes, no NaNs

2. **Evolution consistency**
   - H matches da/dt / a
   - ρ evolution matches w via continuity equation
   - Physical time increases monotonically

3. **Comparison test**
   - ΛCDM-like case: constant w = -1 → compare
   - Matter-like case: w = 0 → compare
   - Transition case: w evolves → document

---

## Observable Targets (Aspirational)

These are NOT acceptance criteria but represent success if achieved:

### Near-term (would be promising)
- w ≈ -1 ± 0.1 (roughly cosmological constant)
- H approximately constant (not wildly varying)
- Acceleration emerges (ä > 0 at late times)

### Medium-term (would be exciting)
- w(z) matches DESI bounds: w(z) = w₀ + wa·z/(1+z)
- H₀ in range [60-80] km/s/Mpc
- No fine-tuning of parameters required

### Long-term (would be revolutionary)
- Explain w crossing -1 (phantom behavior)
- Predict H₀ tension resolution
- Derive Λ ~ 10⁻¹²⁰ from floor dynamics

**Note:** We explicitly do NOT require these targets for Phase 6 acceptance. We simply want to extract observables and see what the framework predicts, whether promising or not.

---

## Risks and Failure Modes

1. **Unphysical w**
   - Risk: w < -1.5 or w > +1 in wrong regime
   - Mitigation: Document, understand why, refine if needed

2. **Diverging H**
   - Risk: H → ∞ or H oscillates wildly
   - Mitigation: Check numerical stability, floor violations

3. **Collapsing a**
   - Risk: a(t) decreases → universe contracts
   - Mitigation: Acceptable if drive is too weak, document finding

4. **No relation to real cosmology**
   - Risk: w ~ +0.5, H ~ negative, completely wrong
   - Mitigation: This is still a valid outcome → framework doesn't describe universe

5. **Non-monotonic time**
   - Risk: Physical time decreases or reverses
   - Mitigation: Check emergent time implementation (Phase 4)

---

## Success Definition

**Phase 6 succeeds if:**
1. All acceptance criteria met (AC1-AC6)
2. Observables extracted without crashes
3. Results documented (match or mismatch with real cosmology)

**Phase 6 is valuable even if:**
- w ≠ -1 (tells us framework is wrong, still knowledge)
- H diverges (tells us instability, still information)
- No match with data (eliminates hypothesis, still progress)

The goal is **honest extraction and comparison**, not forcing agreement.

---

## Connections to Previous Phases

- **Phase 0:** Manifold topology → spatial structure for averaging
- **Phase 1:** Dynamics ∂ψ/∂τ → energy density ρ
- **Phase 2:** Emergent geometry → could define "expansion" as metric growth
- **Phase 3:** Floor constraint → minimum energy (ρ ≥ ρ_floor)
- **Phase 4:** Emergent time → physical time t for H(t), a(t)
- **Phase 5:** Emergent drive → maintains dynamics → sustains ρ

All previous phases feed into cosmological observables.

---

## Implementation Plan

1. Create `phase6_fc/cosmology.py` (~400 lines)
   - CosmologicalObservables class
   - Energy density, H, a, w, P computation
   - Evolution tracking

2. Create `phase6_fc/__init__.py`
   - Export CosmologicalObservables

3. Create comprehensive tests (~500 lines)
   - test_cosmological_observables.py (unit tests)
   - test_cosmology_evolution.py (integration tests)
   - test_observational_comparison.py (comparison with known models)

4. Create acceptance test
   - experiments/phase6_acceptance_test.py
   - Full evolution with observable extraction
   - Comparison with ΛCDM benchmark
   - Generate outputs/phase6_*.csv

5. Create RESULTS.md
   - Observed H(τ), w(τ), a(τ)
   - Comparison with DESI/Planck (qualitative)
   - Findings: promising, unphysical, or ambiguous

---

## Notes

- This phase is where rubber meets road: does framework describe reality?
- Negative results are acceptable and valuable
- We prioritize honest comparison over confirmation bias
- If promising → continue to Phase 7 (parameter constraints)
- If unphysical → document why, potentially revise earlier phases
- If ambiguous → explore parameter space

---

**Status:** Ready to implement
**Dependencies:** Phases 0-5 complete (all ACCEPTED)
**Next:** Implementation begins

---

**Contract maintained by:** Claude
**Approved by:** [Awaiting Human approval to proceed]

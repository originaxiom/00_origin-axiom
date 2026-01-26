# Phase 1_FC Contract: Frustrated Dynamics

**Status:** ✓ ACCEPTED
**Version:** v1.0
**Date:** 2026-01-25
**Accepted:** 2026-01-26

---

## Purpose

Phase 1 implements the **frustrated dynamics** that drive the system's evolution:
- Evolution equations for ψ
- Cancellation tendency (dissipation toward zero)
- Anti-cancel drive (prevents collapse)
- Floor enforcement (prevents |ψ| < ε)
- Energy from striving

**Goal:** Demonstrate that "trying to cancel but can't" produces non-trivial living dynamics, not static frozen states.

---

## Scope

### In Scope

1. **FrustratedDynamics class**
   - Evolution equation: ∂ψ/∂τ = -Γ[ψ] + Drive[ψ] + floor_enforcement
   - Cancellation tendency: -γψ (simple dissipation)
   - Anti-cancel drive: iωψ (rotation) + optional constant drive
   - Floor projection: |ψ| ≥ ε (hard constraint)
   - Energy calculation: E ~ |∂ψ/∂τ|²

2. **Evolution methods**
   - Single timestep evolution
   - Full trajectory evolution
   - Diagnostics (floor hits, energy, global cancellation)

3. **Tests**
   - Floor enforcement works
   - Dynamics are reproducible
   - Energy remains bounded
   - Comparison: with drive vs without drive

### Out of Scope

- ❌ Emergent geometry (Phase 2)
- ❌ Floor derivation (Phase 3)
- ❌ Cosmology extraction (Phase 4)
- ❌ Spatial gradients (Phase 2)
- ❌ Advanced drive mechanisms (future)

---

## Core Objects

### FrustratedDynamics

**Purpose:** Evolve ψ under frustrated cancellation dynamics.

**Minimal interface:**
```python
class FrustratedDynamics:
    def __init__(self, field, gamma, omega, epsilon, drive_amplitude=0.0):
        """
        field: FrustrationField instance
        gamma: dissipation rate
        omega: rotation frequency
        epsilon: floor value (|ψ| ≥ ε)
        drive_amplitude: constant drive magnitude
        """

    def evolve_step(self, dt) -> dict:
        """
        Single evolution step.

        Returns diagnostics:
        - floor_hits: number of nodes hitting floor
        - global_cancel: global cancellation measure
        - mean_amp: mean amplitude
        - energy: energy density from striving
        """

    def evolve_trajectory(self, n_steps, dt, save_every=1) -> DataFrame:
        """
        Evolve for n_steps, save diagnostics.
        """
```

**Evolution equation:**
```
ψ(τ + dt) = ψ(τ) + dt·[−γψ + iωψ + D]
with floor projection: if |ψ| < ε, set |ψ| = ε
```

---

## Design Decisions

### Why Simple Dissipation -γψ?

**Cancellation tendency must:**
- Drive ψ → 0 (attempts to cancel)
- Be smooth and simple
- Not introduce unnecessary structure

**Choice:** Linear dissipation -γψ
- **Pros:** Simple, well-understood, drives to zero
- **Cons:** Not derived from first principles (future work)

**Alternatives considered:**
- Nonlinear: -γψ|ψ|² (more complex, not needed yet)
- Global feedback: -(Σψ)ψ* (couples all nodes, too complex)

### Why Rotation iωψ?

**Anti-cancel drive must:**
- Oppose collapse to zero
- Keep system "alive"
- Be simple to implement

**Choice:** Rotation iωψ + optional constant drive D
- **Pros:**
  - Rotation prevents collapse (perpendicular to dissipation)
  - Constant drive provides ongoing push
  - Together create non-trivial attractors
- **Cons:** Ad-hoc (not derived yet)

**Why not just floor?**
From Phase 0 toy experiments (origin-axiom-framework):
- Floor-only → frozen at |ψ| = ε (85% time on floor)
- Need drive to keep system away from floor

### Why Hard Floor Projection?

**Current approach:** If |ψ| < ε after evolution step, radially project to ε.

**Pros:**
- Simple to implement
- Guarantees |ψ| ≥ ε always
- Clear enforcement

**Cons:**
- Not derived from principles (Phase 3 goal)
- Discontinuous (sudden projection)
- Not physical (yet)

**Future:** Replace with derived floor from holography/topology/information.

### Energy from Striving

**Definition:** E = ⟨|∂ψ/∂τ|²⟩

**Interpretation:**
- Energy is **not** stored in ψ itself
- Energy is the **rate of change** (striving)
- Larger |∂ψ/∂τ| → more vigorous attempt to evolve
- This is the "cost" of frustrated cancellation

**Why this matters:**
- Standard physics: E ~ |ψ|² (field energy)
- Ours: E ~ |dψ/dτ|² (process energy)
- Ontological shift: energy from becoming, not being

---

## Verification

### Tests Required

1. **test_frustrated_dynamics.py:**
   - Initialization works
   - Single step evolution doesn't crash
   - Floor is enforced (no |ψ| < ε)
   - Reproducibility (same seed → same trajectory)
   - Energy remains bounded (no explosion)

2. **test_dynamics_comparison.py:**
   - With drive: system stays alive (not frozen)
   - Without drive: system collapses to floor
   - Energy higher with drive than without

3. **test_integration_phase1.py:**
   - Full workflow (manifold → field → dynamics → evolution)
   - Diagnostics saved correctly
   - Multiple trajectories can be run

### Acceptance Criteria

All tests pass:
```bash
python -m pytest tests/ -v
```

No errors, no warnings.

**Specific targets:**
- Floor violation rate: 0% (all projections successful)
- With drive (D>0, ω>0): floor activity < 20%
- Without drive (D=0, ω=0): floor activity > 50%
- Energy: positive, bounded, stable

---

## Phase 1 Experiments

**Not in scope for contract, but natural next step:**

After Phase 1 acceptance, run:
```python
experiments/frustrated_dynamics_comparison.py
```

This will:
- Run Toy A: dissipation only (no drive)
- Run Toy B: dissipation + rotation + drive
- Compare floor activity, energy, attractors
- Generate plots and CSV tables

Purpose: Document that drive is **necessary** for living dynamics.

---

## Non-Claims

Phase 1 does **not** claim:

- ❌ That this evolution equation describes the actual universe
- ❌ That γ, ω, ε have physical values
- ❌ That the drive is fundamental (it's phenomenological)
- ❌ That the floor derivation is complete
- ❌ That energy E ~ |dψ/dτ|² is measured in experiments

Phase 1 is **mathematical implementation**, not physics claim.

Physics claims require:
- Floor derivation (Phase 3)
- Observable predictions (Phase 4)
- Data comparison

---

## Dependencies

**Requires Phase 0_FC:**
- PreGeometricManifold
- FrustrationField

**Python packages:**
- numpy (arrays, complex numbers)
- pandas (trajectory storage)
- pytest (testing)

**Version requirements:**
- Python >= 3.9
- numpy >= 1.20
- pandas >= 1.3
- pytest >= 7.0

---

## Outputs

**Code:**
- `phase1_fc/dynamics.py`

**Tests:**
- `tests/test_frustrated_dynamics.py`
- `tests/test_dynamics_comparison.py`
- `tests/test_integration_phase1.py`

**Documentation:**
- This contract

**Artifacts:**
- None yet (experiments produce artifacts after contract acceptance)

---

## Next Phase

**Phase 2_FC: Emergent Geometry**

Will add:
- Distance measure from ψ: d(i,j) = f(ψ_i, ψ_j)
- Metric extraction: g_μν from ψ correlations
- Dimension estimation: intrinsic dimension from distances
- Curvature estimate: R ~ ∇²(log|ψ|)

Phase 2 depends on Phase 1 passing all tests.

---

## Acceptance

Phase 1 is **accepted** when:

1. All code written and passes tests ✓
2. Floor enforcement verified (0% violations) ✓
3. Drive necessity demonstrated (with/without comparison) ✓
4. Reviewed and explicitly approved ✓

**Status:** ✓ ACCEPTED (2026-01-26)

---

**Contract status:** ✓ ACCEPTED
**Last updated:** 2026-01-26

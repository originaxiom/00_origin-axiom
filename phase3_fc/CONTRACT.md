# Phase 3_FC Contract: Floor Derivation

**Status:** ACTIVE
**Version:** v1.0
**Date:** 2026-01-26

---

## Purpose

Phase 3 derives the **existence floor** from first principles rather than imposing it as a hard constraint:
- Holographic bound on information capacity
- Information-theoretic limits on cancellation
- Topological constraints from graph structure
- Replace hard floor projection (Phase 1) with derived constraint

**Goal:** Demonstrate that the floor ε is not arbitrary, but emerges from fundamental constraints.

**Critical motivation:** In Phases 0-2, we imposed |ψ| ≥ ε by hand. Now we ask: **why can't ψ cancel completely?**

---

## Scope

### In Scope

1. **Holographic floor estimate**
   - Surface-to-volume ratio on graph
   - Information capacity from boundary
   - Bound: N_states ~ A/ε² (holographic principle analog)
   - Derive minimum ε from N_nodes and graph structure

2. **Information-theoretic floor**
   - Shannon entropy of ψ configuration
   - Minimum entropy to maintain "alive" state
   - Perfect cancellation → zero entropy → forbidden
   - Derive ε from entropy bounds

3. **Topological floor**
   - Graph connectivity constraints
   - Cannot have all nodes cancel if graph is connected
   - Minimum non-zero flow from topology
   - Derive ε from graph Laplacian spectrum

4. **Comparison with hard floor**
   - Compare derived floors with imposed ε=0.01
   - Check consistency: do derived values match?
   - Document which derivation is most stringent

5. **Tests**
   - Floor calculations reproducible
   - Derived floors are finite and positive
   - Holographic/information/topology methods give consistent order of magnitude
   - Integration with Phase 1 dynamics

### Out of Scope

- ❌ Full holographic duality (too ambitious)
- ❌ Quantum information theory (classical approximation only)
- ❌ Cosmology extraction (Phase 4)
- ❌ Experimental predictions (Phase 4)
- ❌ Claims about physical Planck scale
- ❌ Replacing floor in dynamics (keep Phase 1 as-is, just compare)

**Important:** Phase 3 **derives** floor values but does **not** replace the Phase 1 hard floor implementation. That would require re-running all dynamics, which is out of scope. We derive, compare, document.

---

## Core Objects

### FloorDerivation

**Purpose:** Derive existence floor from fundamental constraints.

**Minimal interface:**
```python
class FloorDerivation:
    def __init__(self, manifold: PreGeometricManifold):
        """
        manifold: PreGeometricManifold (topology provides constraints)
        """

    def holographic_floor(self) -> tuple[float, dict]:
        """
        Derive floor from holographic bound.

        Returns: (epsilon_holo, diagnostics)
        """

    def information_floor(self, field: FrustrationField) -> tuple[float, dict]:
        """
        Derive floor from information entropy.

        Returns: (epsilon_info, diagnostics)
        """

    def topological_floor(self) -> tuple[float, dict]:
        """
        Derive floor from graph topology.

        Returns: (epsilon_topo, diagnostics)
        """

    def compare_floors(self, epsilon_imposed: float) -> pd.DataFrame:
        """
        Compare derived floors with imposed value.

        Returns: DataFrame with all floor values and ratios
        """
```

---

## Derivation Methods

### Method 1: Holographic Floor

**Motivation:** Holographic principle: information in volume V is bounded by surface area A.

**Graph analog:**
- Volume: N_nodes
- Surface: Number of boundary-adjacent edges (or total degree)
- Holographic bound: S ≤ A / (4ℓ_P²) in Planck units

**Derivation:**

For discrete graph:
```
Surface area (discrete) ~ sqrt(N) for cubic 3D
Volume ~ N
Holographic ratio: A/V ~ N^(-1/2)
```

If each node stores information ~ log(1/ε) (quantization resolution):
```
Total information: I_total ~ N·log(1/ε)
Holographic bound: I_total ≤ C·sqrt(N)
Therefore: N·log(1/ε) ≤ C·sqrt(N)
Solving: ε_holo ~ exp(-C/sqrt(N))
```

For small systems, approximately: **ε_holo ~ 1/sqrt(N)**.

**Pros:**
- Connects to holographic principle
- Dimensionally consistent
- Predicts floor scales with system size

**Cons:**
- Graph "surface area" not rigorously defined
- Holographic principle is quantum gravity, not classical
- Coefficient C is order-of-magnitude

### Method 2: Information-Theoretic Floor

**Motivation:** Perfect cancellation → all ψ_i → 0 → zero information → degenerate.

**Derivation:**

Shannon entropy of amplitude distribution:
```
S = -Σ p_i log(p_i)
where p_i = |ψ_i|² / Σ|ψ_j|²
```

For system to be "alive":
```
S > S_min (some minimum entropy to maintain complexity)
```

If all |ψ_i| → ε (floor), entropy:
```
S_uniform = log(N) (maximum for uniform distribution)
```

If all |ψ_i| → 0, entropy → 0 (degenerate).

Require: S > S_min ~ log(N_eff) where N_eff < N.

This gives: **ε_info ~ (S_min / N)^(1/2)** for order of magnitude.

**Pros:**
- Information-theoretic (no quantum gravity)
- Well-defined for discrete systems
- Captures "complexity" requirement

**Cons:**
- S_min is not first-principles derived
- Depends on field state (not just manifold)
- Entropy measure choice arbitrary

### Method 3: Topological Floor

**Motivation:** Connected graph cannot have all ψ → 0 simultaneously if edges impose constraints.

**Derivation:**

Graph Laplacian: L = D - A (degree matrix minus adjacency).

Laplacian eigenvalues: λ_0 = 0, λ_1 > 0, ..., λ_{N-1}.

For connected graph, λ_1 > 0 (algebraic connectivity).

If we model "flow" on graph as f = -L·ψ (diffusion), then minimum non-zero flow:
```
||f||² = ψ^T L ψ ≥ λ_1 ||ψ||²
```

For flow to exist: ψ cannot be uniform zero.

Minimum amplitude: **ε_topo ~ sqrt(λ_1 / N)** (order of magnitude).

For cubic 3D lattice: λ_1 ~ 1 (graph-dependent), so ε_topo ~ 1/sqrt(N).

**Pros:**
- Uses only graph structure
- No ad-hoc parameters
- Rigorously computable from adjacency

**Cons:**
- Connection to "existence floor" is heuristic
- Laplacian eigenvalue doesn't directly forbid ψ=0
- Interpretation as minimum amplitude is not rigorous

---

## Design Decisions

### Why Not Replace Phase 1 Floor?

**Rationale:** Replacing the hard floor in FrustratedDynamics would require:
- Re-implementing floor enforcement with derived value
- Re-running all Phase 1 tests and experiments
- Re-generating Phase 1 evidence artifacts
- Potential breaking changes to dynamics

**Instead:** Phase 3 **derives** floor values and **compares** with imposed ε=0.01:
- Derive ε_holo, ε_info, ε_topo
- Compare with ε_imposed = 0.01
- Document consistency (or lack thereof)
- If consistent: validates imposed choice
- If inconsistent: identifies tension

**Future work:** Soft floor implementation could use derived values.

### Why Three Methods?

**Rationale:** We don't know which derivation is "correct". By implementing three:
- Cross-check consistency
- Identify which is most stringent
- Stay honest about multiple approaches
- Document all derivations, let data decide

If all three give ε ~ 0.01, strong evidence floor is not arbitrary.
If they differ by orders of magnitude, indicates one approach is wrong or missing physics.

### Why Order-of-Magnitude?

**Rationale:** These are **heuristic** derivations, not rigorous proofs:
- Holographic principle applies to quantum gravity, not classical fields
- Information entropy depends on measure choice
- Topological constraint is suggestive, not definitive

**Acceptance criterion:** Derived floors should be **same order of magnitude** (within factor of 10) as imposed ε=0.01. Exact match is not expected.

---

## Verification

### Tests Required

1. **test_floor_derivation.py:**
   - Holographic floor computes correctly
   - Information floor computes correctly
   - Topological floor computes correctly
   - All floors are finite and positive
   - Reproducibility

2. **test_floor_comparison.py:**
   - Derived floors compared with imposed floor
   - Order-of-magnitude consistency check
   - Different system sizes (does ε scale correctly?)

3. **test_integration_phase3.py:**
   - Full workflow: manifold → field → dynamics → geometry → floor derivation
   - Floor derivation integrates with previous phases

### Acceptance Criteria

All tests pass:
```bash
python -m pytest tests/ -v
```

**Specific targets:**
- All derived floors positive: ε_holo, ε_info, ε_topo > 0
- All derived floors bounded: 1e-6 < ε < 1e0
- Order-of-magnitude consistency: 0.1·ε_imposed < ε_derived < 10·ε_imposed (within factor 10)
- Reproducible with fixed seeds
- No NaN or Inf

**Stretch goal (not required for acceptance):**
- All three methods agree within factor of 3

---

## Design Decisions Log

### Why Derive Floor After Dynamics?

**Rationale:** Logical structure:
1. Phase 0: Manifold (no metric, no floor)
2. Phase 1: Dynamics (impose floor to see what happens)
3. Phase 2: Geometry (extract structure from field)
4. Phase 3: Floor (justify imposed constraint) ← **we are here**
5. Phase 4: Cosmology (make predictions)

**Why this order?**
- Needed dynamics (Phase 1) to see floor is necessary (100% collapse without drive)
- Needed geometry (Phase 2) to see emergent structure
- Now ask: can we derive the floor from principles?

**Alternative order:** Derive floor first, then impose in dynamics.
**Rejected because:** We wouldn't know if floor is necessary without running dynamics first.

### What Counts as "Derived"?

**Strict definition:** First-principles calculation from axioms with no free parameters.

**Realistic definition:** Heuristic calculation from plausible physical constraints (holography, information, topology) with order-of-magnitude coefficients.

**Phase 3 uses realistic definition.** We are not claiming rigorous derivation, but showing plausible bounds.

---

## Non-Claims

Phase 3 does **not** claim:

- ❌ That holographic principle applies to this system
- ❌ That information entropy is the "correct" measure
- ❌ That topological constraint is fundamental
- ❌ That derived floor is exact value (order-of-magnitude only)
- ❌ That floor derivation is rigorous proof
- ❌ That ε_imposed = 0.01 was correct choice

Phase 3 is **plausibility argument**, not fundamental theorem.

Physics claims require:
- Full holographic duality (beyond scope)
- Quantum field theory (we're classical)
- Observable predictions (Phase 4)

---

## Dependencies

**Requires Phase 0_FC + Phase 1_FC + Phase 2_FC:**
- PreGeometricManifold (topology, adjacency, Laplacian)
- FrustrationField (ψ state for information entropy)
- FrustratedDynamics (imposed floor for comparison)
- EmergentGeometry (context, not directly used)

**Python packages:**
- numpy (eigenvalues, linear algebra)
- scipy (sparse matrices, eigenvalue solvers)
- pandas (comparison tables)
- pytest (testing)

**Version requirements:**
- Python >= 3.9
- numpy >= 1.20
- scipy >= 1.7
- pandas >= 1.3
- pytest >= 7.0

---

## Outputs

**Code:**
- `phase3_fc/derivation.py` — FloorDerivation class

**Tests:**
- `tests/test_floor_derivation.py` — Basic derivations
- `tests/test_floor_comparison.py` — Comparison with imposed floor
- `tests/test_integration_phase3.py` — Full workflow

**Documentation:**
- This contract
- `phase3_fc/RESULTS.md` (after acceptance tests)

**Artifacts:**
- Floor comparison tables
- Scaling analysis (ε vs N)

---

## Experiments (Post-Acceptance)

After Phase 3 acceptance, optional experiments:

1. **Scaling analysis:** Derive floors for N = 27, 64, 125, 343. Check ε ~ N^α scaling.
2. **Floor comparison plots:** Visualize all four floors (holo, info, topo, imposed).
3. **Consistency analysis:** Which derivation gives closest match to imposed floor?

These are **not** required for acceptance, but natural follow-up.

---

## Next Phase

**Phase 4_FC: Cosmology Extraction**

Will add:
- Effective FLRW metric from emergent geometry
- Scale factor evolution from ψ dynamics
- Equation of state w(z) extraction
- Comparison with DESI 2024 data

Phase 4 depends on Phase 3 passing all tests.

---

## Acceptance

Phase 3 is **accepted** when:

1. All code written and passes tests
2. All derived floors positive and bounded
3. Order-of-magnitude consistency with imposed floor
4. Comparison documented with binding evidence
5. Reviewed and explicitly approved

Until then: **provisional**.

---

**Contract status:** ACTIVE
**Last updated:** 2026-01-26

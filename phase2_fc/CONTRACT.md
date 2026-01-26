# Phase 2_FC Contract: Emergent Geometry

**Status:** ACTIVE
**Version:** v1.0
**Date:** 2026-01-26

---

## Purpose

Phase 2 extracts **emergent geometric structure** from the frustration field ψ:
- Distance measure from ψ correlations
- Effective metric tensor
- Intrinsic dimension estimation
- Curvature estimate

**Goal:** Demonstrate that geometric structure can emerge from ψ dynamics, rather than being assumed a priori.

**Critical distinction:** We built the manifold with discrete topology (Phase 0) but **no metric**. Now we ask: does ψ induce a distance structure?

---

## Scope

### In Scope

1. **EmergentGeometry class**
   - Distance measure: d(i,j) = f(ψ_i, ψ_j, correlations)
   - Effective metric: g_eff from local distance gradients
   - Dimension estimate: intrinsic dimension from distance scaling
   - Curvature estimate: R ~ ∇²(log|ψ|) or Ricci scalar approximation

2. **Distance measures to explore**
   - Amplitude difference: d ~ |ψ_i - ψ_j|
   - Phase coherence: d ~ 1 - Re(ψ_i* ψ_j / |ψ_i||ψ_j|)
   - Hybrid: combination of amplitude and phase
   - Graph geodesic weighted by ψ

3. **Diagnostics**
   - Distance matrix (sparse, only neighbors or sample)
   - Dimension estimation via scaling analysis
   - Curvature distribution
   - Metric signature (if extractable)

4. **Tests**
   - Distance measure properties (symmetry, triangle inequality)
   - Dimension recovery on known topologies
   - Reproducibility
   - Integration with Phase 0 + Phase 1

### Out of Scope

- ❌ Full Riemannian manifold (just effective local metric)
- ❌ Geodesic computation (too expensive, future work)
- ❌ Cosmology extraction (Phase 4)
- ❌ Claims about physical spacetime (not yet)
- ❌ Floor derivation (Phase 3)
- ❌ Connection to observables (Phase 4)

---

## Core Objects

### EmergentGeometry

**Purpose:** Extract geometric structure from ψ field.

**Minimal interface:**
```python
class EmergentGeometry:
    def __init__(self, field: FrustrationField, method: str = 'hybrid'):
        """
        field: FrustrationField instance (with evolved ψ)
        method: Distance measure ('amplitude', 'phase', 'hybrid')
        """

    def compute_distance_matrix(self, mode: str = 'neighbors') -> np.ndarray:
        """
        Compute distance matrix.

        mode: 'neighbors' (only adjacent nodes) or 'sample' (random pairs)
        Returns: distance matrix or list of (i, j, d_ij)
        """

    def estimate_dimension(self) -> tuple[float, dict]:
        """
        Estimate intrinsic dimension from distance scaling.

        Returns: (estimated_dim, diagnostics)
        """

    def estimate_curvature(self) -> tuple[float, np.ndarray]:
        """
        Estimate curvature scalar.

        Returns: (mean_curvature, curvature_field)
        """

    def effective_metric_local(self, node: int) -> np.ndarray:
        """
        Estimate local effective metric at node.

        Returns: g_eff (small matrix, e.g. 3x3 if embedded in R^3)
        """
```

---

## Distance Measures

### Design Decisions

We have several options for defining distance from ψ. Each has trade-offs.

### Option 1: Amplitude Difference

```
d_ij = |ψ_i - ψ_j|
```

**Pros:**
- Simple, intuitive
- Sensitive to amplitude structure
- Metric properties (triangle inequality, symmetry)

**Cons:**
- Ignores phase information
- May not capture rotation dynamics

### Option 2: Phase Coherence

```
d_ij = sqrt(2(1 - Re(ψ_i* ψ_j / |ψ_i||ψ_j|)))
```

This measures phase alignment.

**Pros:**
- Captures phase structure (important for rotation dynamics)
- Natural for complex fields
- Bounded: [0, 2]

**Cons:**
- Insensitive to amplitude
- Degenerates when |ψ| ≈ 0

### Option 3: Hybrid (Recommended)

```
d_ij = sqrt(|ψ_i - ψ_j|² + λ·(1 - Re(ψ_i* ψ_j / |ψ_i||ψ_j|)))
```

Combines amplitude and phase with weight λ.

**Pros:**
- Captures both amplitude and phase structure
- Tunable via λ
- Reduces to amplitude or phase in limits

**Cons:**
- One more parameter to choose
- Interpretation less direct

**Choice for Phase 2:** Implement all three, default to hybrid with λ=1.

---

## Dimension Estimation

### Method: Box-counting or Correlation Dimension

**Correlation dimension approach:**

1. Sample pairs of nodes (i, j)
2. Compute distances d_ij
3. Count pairs within distance r: C(r) = #(d_ij < r) / N_pairs
4. Fit: C(r) ~ r^D_corr
5. Estimate D_corr from log-log slope

**Expected results:**
- Cubic 3D lattice: D ≈ 3
- Random graph: D ~ log(N) (high-dimensional)
- After ψ evolution: D may differ from topology

**Key question:** Does ψ dynamics induce effective dimension different from topology?

---

## Curvature Estimation

### Method: Discrete Laplacian Approximation

For scalar curvature estimate:

```
R_i ≈ -∇²(log|ψ_i|)
```

Discrete Laplacian on graph:
```
∇²f_i = (1/k_i) Σ_{j∈N(i)} (f_j - f_i)
```

where k_i = degree of node i.

**Pros:**
- Simple to compute
- Uses only nearest neighbors
- Natural on graph structure

**Cons:**
- Not rigorous curvature (no full metric)
- Interpretation as scalar curvature is heuristic
- Sensitive to noise

**Acceptance criterion:** Demonstrate non-trivial curvature structure (not uniform).

---

## Verification

### Tests Required

1. **test_emergent_geometry.py:**
   - Distance symmetry: d_ij = d_ji
   - Triangle inequality (at least approximately)
   - Distance positivity: d_ii = 0, d_ij > 0 for i≠j
   - Reproducibility with fixed seeds

2. **test_geometry_measures.py:**
   - Dimension estimation on cubic lattice (expect D≈3)
   - Dimension on random graph
   - Curvature computation doesn't crash
   - Curvature has finite values

3. **test_integration_phase2.py:**
   - Full workflow: manifold → field → dynamics → geometry
   - Distance matrix computes correctly
   - Metrics are finite and reasonable

### Acceptance Criteria

All tests pass:
```bash
python -m pytest tests/ -v
```

**Specific targets:**
- Distance properties verified (symmetry, positivity, triangle inequality within tolerance)
- Dimension estimate for cubic 3D: 2.5 < D < 3.5
- Curvature values finite and bounded: |R| < 100
- No NaN or Inf in any geometry measure
- Reproducible results with fixed seeds

---

## Design Decisions Log

### Why Not Assume Metric?

**Rationale:** If we assume FRW metric from the start, we cannot claim geometry emerges. We must:
1. Start with discrete topology only (Phase 0) ✓
2. Evolve ψ dynamics (Phase 1) ✓
3. Extract distance/metric from ψ (Phase 2) ← **we are here**
4. Check if extracted geometry matches cosmological observations (Phase 4)

This is the only way to test "geometry from field" rather than "field on geometry."

### Why Multiple Distance Measures?

**Rationale:** We don't know a priori which distance measure is "correct." By implementing several:
- We can compare which gives most coherent dimension/curvature
- We stay honest about arbitrary choices
- Future work can explore which measure (if any) produces physical predictions

### Why Not Full Riemannian Geometry?

**Rationale:** Computing full metric tensor g_μν(x) on discrete graph with N~100-1000 nodes is:
- Computationally expensive (need many local distance measurements)
- Under-constrained (graph has finite neighbors, not continuous manifold)
- Not needed for Phase 2 acceptance

We only compute:
- Distance matrix (sparse)
- Dimension estimate (scalar)
- Curvature estimate (field R_i)
- Local metric samples (for validation)

Full metric extraction is future work.

---

## Non-Claims

Phase 2 does **not** claim:

- ❌ That extracted geometry is the physical spacetime
- ❌ That dimension D is exactly 3 or 4
- ❌ That curvature R connects to Einstein equations
- ❌ That distance measure is unique or fundamental
- ❌ That metric signature is Lorentzian
- ❌ That we've derived the metric (it's extracted, not derived)

Phase 2 is **exploratory implementation**, not physics claim.

Physics claims require:
- Floor derivation (Phase 3)
- Observable predictions (Phase 4)
- Data comparison

---

## Dependencies

**Requires Phase 0_FC + Phase 1_FC:**
- PreGeometricManifold (topology)
- FrustrationField (ψ on manifold)
- FrustratedDynamics (evolved ψ)

**Python packages:**
- numpy (linear algebra, distances)
- scipy (optional: spatial.distance, optimize for fitting)
- pandas (trajectory storage)
- pytest (testing)

**Version requirements:**
- Python >= 3.9
- numpy >= 1.20
- scipy >= 1.7 (optional)
- pandas >= 1.3
- pytest >= 7.0

---

## Outputs

**Code:**
- `phase2_fc/geometry.py` — EmergentGeometry class

**Tests:**
- `tests/test_emergent_geometry.py` — Basic geometry properties
- `tests/test_geometry_measures.py` — Dimension and curvature
- `tests/test_integration_phase2.py` — Full workflow

**Documentation:**
- This contract
- `phase2_fc/RESULTS.md` (after acceptance tests)

**Artifacts:**
- Distance matrices (samples, not full N×N)
- Dimension estimates
- Curvature distributions

---

## Experiments (Post-Acceptance)

After Phase 2 acceptance, optional experiments:

1. **Dimension evolution:** Does D change as ψ evolves?
2. **Curvature-amplitude correlation:** Is R correlated with |ψ|?
3. **Distance measure comparison:** Which distance gives most coherent D?
4. **Topology dependence:** Does cubic vs random graph produce different emergent D?

These are **not** required for acceptance, but natural next questions.

---

## Next Phase

**Phase 3_FC: Floor Derivation**

Will add:
- Holographic floor derivation
- Information-theoretic bounds
- Topological constraints
- Replace hard floor with derived floor

Phase 3 depends on Phase 2 passing all tests.

---

## Acceptance

Phase 2 is **accepted** when:

1. All code written and passes tests
2. Distance properties verified (symmetry, positivity, triangle inequality)
3. Dimension estimation works (reasonable values on test cases)
4. Curvature estimation computes (finite, bounded values)
5. Reviewed and explicitly approved

Until then: **provisional**.

---

**Contract status:** ACTIVE
**Last updated:** 2026-01-26

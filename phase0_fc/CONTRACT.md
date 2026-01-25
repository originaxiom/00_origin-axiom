# Phase 0_FC Contract: Pre-Geometric Foundation

**Status:** ACTIVE (bootstrap phase)
**Version:** v1.0
**Date:** 2026-01-25

---

## Purpose

Phase 0 establishes the **pre-geometric foundation** for frustrated cancellation dynamics:
- Discrete manifold structure (topology without metric)
- Complex field ψ living on manifold
- Basic measurements (amplitudes, phases, cancellation)

**Goal:** Provide minimal structure on which to implement frustrated dynamics **without** assuming spacetime geometry exists a priori.

---

## Scope

### In Scope

1. **PreGeometricManifold class**
   - Discrete graph/lattice topology
   - Node connectivity (adjacency)
   - Multiple topology options (cubic, random, etc.)
   - NO coordinates, NO metric, NO distances

2. **FrustrationField class**
   - Complex amplitude ψ_i at each node i
   - Initialization (random, structured)
   - Global cancellation measure
   - Phase and amplitude accessors

3. **Basic tests**
   - Topology builds correctly
   - Field initializes reproducibly
   - Cancellation measure behaves as expected
   - Random seed control works

### Out of Scope

- ❌ Dynamics (Phase 1)
- ❌ Floor enforcement (Phase 1)
- ❌ Geometry extraction (Phase 2)
- ❌ Floor derivation (Phase 3)
- ❌ Observable predictions (Phase 4)

---

## Core Objects

### PreGeometricManifold

**Purpose:** Discrete space without assuming metric or coordinates.

**Minimal interface:**
```python
class PreGeometricManifold:
    def __init__(self, N_nodes, topology='cubic_3d'):
        """
        N_nodes: number of discrete points
        topology: connectivity pattern
        """

    @property
    def N(self) -> int:
        """Number of nodes"""

    @property
    def adjacency(self) -> dict[int, list[int]]:
        """Node i → list of neighbor indices"""
```

**Topologies supported:**
- `cubic_3d`: 3D cubic lattice (6 neighbors per interior node)
- `random_graph`: Erdős-Rényi random graph
- Future: `triangular`, `hexagonal`, `voronoi`

**What is NOT included:**
- Coordinates (x, y, z)
- Metric tensor
- Distances
- Curvature

These emerge later (Phase 2) from ψ structure.

### FrustrationField

**Purpose:** Complex field ψ on manifold.

**Minimal interface:**
```python
class FrustrationField:
    def __init__(self, manifold, seed=None):
        """
        manifold: PreGeometricManifold instance
        seed: random seed for reproducibility
        """

    @property
    def psi(self) -> np.ndarray:
        """Complex amplitudes, shape (N,)"""

    def initialize_random(self, r_mean, r_std):
        """Random initialization with normal amplitude distribution"""

    def global_cancellation_measure(self) -> float:
        """
        C = |∑_i ψ_i| / (∑_i |ψ_i|)
        C=0: perfect cancellation
        C=1: no cancellation
        """
```

**What is NOT included:**
- Time evolution (Phase 1)
- Floor enforcement (Phase 1)
- Energy calculation (Phase 1)
- Geometry extraction (Phase 2)

---

## Verification

### Tests Required

1. **test_manifold.py:**
   - Cubic lattice has correct neighbor count
   - Adjacency is symmetric
   - Random graph has expected edge density

2. **test_field.py:**
   - Field initializes with correct shape
   - Random seed produces reproducible state
   - Global cancellation scales as N^{-1/2} for random

3. **test_integration.py:**
   - Field can be created on manifold
   - Basic operations don't crash

### Acceptance Criteria

All tests pass:
```bash
python -m pytest tests/ -v
```

No errors, no warnings.

---

## Design Decisions

### Why Discrete (Not Continuum)?

1. **Computational:** Discrete is implementable
2. **Conceptual:** Avoids infinities from continuum field theory
3. **Holographic:** Discrete matches holographic entropy scaling
4. **Pragmatic:** Continuum limit can be approached later

### Why No Coordinates?

**Coordinates (x, y, z) assume:**
- Pre-existing notion of "dimension"
- Embedding space
- Distance metric

**We want geometry to emerge from ψ**, not be imposed.

So we use **graph topology only**:
- Nodes connected by edges
- Adjacency defines "neighbor"
- No distances yet

This is analogous to:
- Lattice QFT (discrete spacetime)
- Causal set theory (discrete causal structure)
- Loop quantum gravity (spin networks)

### Why Complex ψ?

**Phase θ encodes:**
- Twist (related to θ* parameter)
- Rotation (potential source of drive)
- Interference (cancellation structure)

**Amplitude |ψ| encodes:**
- "How much" of reality is here
- Floor constraint target
- Energy density proxy

**Together:** ψ = |ψ|e^{iθ} gives rich structure.

---

## Non-Claims

Phase 0 does **not** claim:

- ❌ That discrete topology describes actual spacetime
- ❌ That ψ is a physical field
- ❌ That N_nodes has physical meaning
- ❌ That adjacency corresponds to light cones
- ❌ That global cancellation measure has observational meaning

Phase 0 is **mathematical infrastructure**, not physics.

Physics claims begin in Phase 1 (if at all).

---

## Dependencies

**Python packages:**
- numpy (arrays, complex numbers)
- pytest (testing)

**External:**
- None

**Version requirements:**
- Python >= 3.9
- numpy >= 1.20
- pytest >= 7.0

---

## Outputs

**Code:**
- `phase0_fc/manifold.py`
- `phase0_fc/field.py`

**Tests:**
- `tests/test_manifold.py`
- `tests/test_field.py`
- `tests/test_integration.py`

**Documentation:**
- This contract

**Artifacts:**
- None (Phase 0 is infrastructure only)

---

## Next Phase

**Phase 1_FC: Frustrated Dynamics**

Will add:
- Evolution equations: ∂ψ/∂τ = ...
- Cancellation tendency: -Γ[ψ]
- Anti-cancel drive: +Drive[ψ, θ*]
- Floor enforcement: |ψ| ≥ ε
- Energy from striving: E ~ |∂ψ/∂τ|²

Phase 1 depends on Phase 0 passing all tests.

---

## Acceptance

Phase 0 is **accepted** when:

1. All code written and passes tests
2. Human reviews and says: **"ACCEPT PHASE 0"**
3. Contract locked (no further edits without errata rung)

Until then: **provisional**.

---

**Contract status:** ACTIVE
**Last updated:** 2026-01-25

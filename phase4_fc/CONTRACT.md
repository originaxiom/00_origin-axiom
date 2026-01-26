# Phase 4_FC Contract: Emergent Time and Causality

**Status:** ACTIVE
**Version:** v1.0
**Date:** 2026-01-26

---

## Purpose

Phase 4 derives **physical time** from the frustrated cancellation dynamics rather than treating time as an external parameter.

- Evolution parameter τ is abstract (just counts steps)
- Physical time dt should emerge from the striving itself
- Time = "progress of the cancellation attempt" (per vision)
- Define observable time from field evolution

**Goal:** Show that time emerges from |dψ|, not imposed externally.

**Critical motivation:** We've been using τ as if it were time, but the vision says time should *emerge* from the dynamics. Phase 4 makes this concrete.

---

## Scope

### In Scope

1. **Physical time definition**
   - Define dt from field evolution: dt ~ f(|dψ|)
   - Options: dt ~ |dψ|, dt ~ √⟨|dψ|²⟩, dt ~ ⟨|∂ψ/∂τ|⟩
   - Must be observable (measurable from ψ trajectory)
   - Must be monotonic (time flows forward)

2. **Time dilation effects**
   - Regions with faster striving → faster time passage
   - Regions near floor (low activity) → slower time
   - Emergent "gravitational" time dilation from field gradients
   - Compare: GR time dilation from metric vs our time dilation from striving

3. **Causality structure**
   - Define causal ordering from ψ evolution
   - Lightcone-like structure: which events can influence which
   - Check: does frustration preserve causality?
   - Verify: no closed timelike curves in reasonable configurations

4. **Age of system**
   - Integrate physical time: T = ∫ dt
   - Compare to number of evolution steps N_steps
   - Check: does T/N_steps vary with dynamics?
   - Derive "age" from accumulated striving

5. **Tests**
   - Time is monotonic (never decreases)
   - Time is approximately uniform for weak fields
   - Time varies spatially for strong gradients
   - Causality preserved under evolution
   - Reproducibility with fixed seeds

### Out of Scope

**Not in Phase 4:**
- Connection to cosmological time (H, a(t), etc.) → Future phase
- Wheeler-DeWitt equation → Too advanced
- Quantum time operator → Quantum version not yet developed
- Thermodynamic arrow of time → Separate concept
- Coordinate time vs proper time distinction → Too GR-specific

### Non-Claims

**We do NOT claim:**
- That this is "the" definition of time in fundamental physics
- That this resolves all conceptual issues with time
- That this reproduces GR time exactly
- That observers would experience this time linearly
- That this explains psychological time perception

---

## Core Objects

### EmergentTime

**Purpose:** Compute physical time from field evolution.

**Initialization:**
```python
class EmergentTime:
    def __init__(self, field: FrustrationField):
        """
        Initialize time tracker for given field.

        Parameters
        ----------
        field : FrustrationField
            Field whose evolution defines time
        """
```

**Key methods:**

#### 1. Physical time increment

```python
def compute_dt(
    self,
    psi_before: np.ndarray,
    psi_after: np.ndarray,
    dtau: float
) -> float:
    """
    Compute physical time increment from field change.

    Physical time defined by "progress of striving":
        dt ~ ⟨|Δψ|⟩ or ⟨|∂ψ/∂τ|⟩

    Parameters
    ----------
    psi_before : ndarray
        Field before evolution step
    psi_after : ndarray
        Field after evolution step
    dtau : float
        Evolution parameter step size

    Returns
    -------
    dt : float
        Physical time increment (>0)
    """
```

#### 2. Local time rate

```python
def local_time_rate(
    self,
    node_idx: int,
    psi: np.ndarray,
    dpsi_dtau: np.ndarray
) -> float:
    """
    Compute local rate of time passage at node.

    Rate = |∂ψ_i/∂τ| (faster striving → faster time)

    Parameters
    ----------
    node_idx : int
        Node index
    psi : ndarray
        Current field
    dpsi_dtau : ndarray
        Time derivative of field

    Returns
    -------
    time_rate : float
        Local time dilation factor (dt/dτ at node)
    """
```

#### 3. Accumulated age

```python
def integrate_time(
    self,
    trajectory: pd.DataFrame
) -> Tuple[float, np.ndarray]:
    """
    Integrate physical time over trajectory.

    T = ∫ dt = ∫ f(|dψ/dτ|) dτ

    Parameters
    ----------
    trajectory : DataFrame
        Evolution trajectory with psi at each step

    Returns
    -------
    total_age : float
        Total accumulated physical time
    time_array : ndarray
        Physical time at each step
    """
```

#### 4. Causality check

```python
def check_causality(
    self,
    psi_trajectory: List[np.ndarray],
    adjacency: Dict[int, List[int]]
) -> Dict[str, Any]:
    """
    Verify causal structure from evolution.

    Check:
    - Information propagates along edges only
    - No closed causal loops
    - Lightcone-like structure emerges

    Parameters
    ----------
    psi_trajectory : list of ndarray
        Field at each time step
    adjacency : dict
        Manifold connectivity

    Returns
    -------
    causality_report : dict
        - violations: number of causality violations
        - max_influence_speed: maximum propagation speed
        - causal_structure: adjacency of causal graph
    """
```

---

## Acceptance Criteria

Phase 4 is complete when:

### 1. Physical Time Definition

- [ ] dt computed from field evolution
- [ ] dt > 0 always (monotonic)
- [ ] dt ≈ constant for uniform weak fields
- [ ] dt varies for strong gradients (time dilation)

### 2. Spatial Variation

- [ ] Time rate varies across nodes: different |∂ψ/∂τ|
- [ ] Regions near floor have slower time (low activity)
- [ ] Regions with strong drive have faster time
- [ ] Time dilation factor measurable: (dt/dτ)_i / (dt/dτ)_j

### 3. Causality

- [ ] Information propagates locally (nearest neighbors)
- [ ] No closed causal loops detected
- [ ] Influence speed bounded by connectivity
- [ ] Causal structure consistent with topology

### 4. Age Calculation

- [ ] Total age T integrates correctly
- [ ] T/N_steps varies with dynamics parameters
- [ ] Age independent of τ step size (dtau) for small dtau
- [ ] Reproducible with fixed seeds

### 5. Tests

- [ ] Unit tests for dt computation
- [ ] Tests for local time rate
- [ ] Integration tests for age calculation
- [ ] Causality verification tests
- [ ] Full Phase 0→4 workflow test

---

## Technical Specifications

### Time Definition Options

**Option 1: Mean field change**
```
dt = ⟨|Δψ|⟩ = (1/N) Σ |ψ_i(τ+Δτ) - ψ_i(τ)|
```
Pro: Simple, intuitive
Con: Depends on Δτ choice

**Option 2: Mean time derivative**
```
dt = ⟨|∂ψ/∂τ|⟩ · dτ = (1/N) Σ |∂ψ_i/∂τ| · dτ
```
Pro: Independent of Δτ, matches energy definition
Con: Requires computing derivative

**Option 3: Energy-based**
```
dt = √⟨|∂ψ/∂τ|²⟩ · dτ = √E · dτ
```
Pro: Connects time to energy, relativistic analog
Con: More abstract

**Recommendation:** Start with Option 2 (mean derivative), compare with Option 3.

### Local Time Dilation

```
(dt/dτ)_i = |∂ψ_i/∂τ|
```

Ratio between two nodes:
```
α_ij = (dt/dτ)_i / (dt/dτ)_j
```

If α > 1: node i ages faster than node j.

### Causality

**Influence speed:** Maximum distance information can propagate in one τ step.

For nearest-neighbor dynamics (∂ψ_i/∂τ depends on ψ_j for j ∈ neighbors(i)):
- Information propagates 1 edge per step
- "Speed of light" = 1 edge per unit τ
- Check: does |∂ψ_i/∂τ| depend only on local neighbors?

**Causal graph:** Directed graph G where edge (i,j) exists if ψ_j(τ) influences ψ i(τ+Δτ).

---

## Files to Create

### Implementation

- `phase4_fc/time.py` — EmergentTime class
- `phase4_fc/__init__.py` — Package interface
- `phase4_fc/CONTRACT.md` — This file

### Tests

- `tests/test_emergent_time.py` — Time computation tests
- `tests/test_time_dilation.py` — Local variation tests
- `tests/test_causality.py` — Causal structure tests
- `tests/test_integration_phase4.py` — Full workflow tests

### Evidence

- `experiments/phase4_acceptance_test.py` — Acceptance test script
- `phase4_fc/RESULTS.md` — Observed results and findings

---

## Success Criteria

Phase 4 succeeds if:

1. **Physical time emerges naturally** from striving dynamics
2. **Time dilation** observed: time rate varies with striving intensity
3. **Causality preserved** under evolution
4. **Age calculation** shows meaningful accumulated time
5. **All tests pass** with reproducible results

Phase 4 fails if:

- Time goes backwards (dt < 0)
- Time is always uniform (no interesting structure)
- Causality violations occur
- Age diverges or becomes negative
- Tests reveal fundamental inconsistency

---

## Dependencies

**Requires:**
- Phase 0: PreGeometricManifold, FrustrationField
- Phase 1: FrustratedDynamics (to compute ∂ψ/∂τ)
- Phase 2: EmergentGeometry (for spatial structure)

**Used by:**
- Future cosmology phases (H(t), a(t))
- Observable predictions

---

## Notes

### Connection to Vision

Vision says: "Time: Progress of the cancellation attempt"

This means:
- Time is not external parameter
- Time measures how much cancellation has been attempted
- Faster striving → more time passes
- No striving (frozen at floor) → time stops

### Comparison to GR

**GR:** Time from metric: dτ² = g_μν dx^μ dx^ν
**FC:** Time from striving: dt ~ |∂ψ/∂τ|

Both allow time dilation, but:
- GR: dilation from spacetime curvature
- FC: dilation from field gradient intensity

### Philosophical Note

If time emerges from striving, then:
- "Before time" = no striving yet
- "End of time" = if striving stops (impossible with drive)
- "Frozen time" = at floor with no drive

This inverts the usual picture: time doesn't flow independently; time IS the flow of attempted cancellation.

---

**Status:** Ready for implementation
**Next:** Implement EmergentTime class and tests

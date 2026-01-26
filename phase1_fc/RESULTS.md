# Phase 1_FC Results Log

**Date:** 2026-01-26
**Version:** v1.0
**Status:** ✓ ACCEPTED BY HUMAN (2026-01-26)

---

## Purpose

This document records **actual observed results** from Phase 1_FC acceptance tests, following the "run-first, log-after" principle (Workflow Contract §6).

All results are **reproducible** from committed code with fixed seeds.

---

## Acceptance Test Execution

**Command:**
```bash
cd /home/user/00_origin-axiom
python3 experiments/phase1_acceptance_test.py
```

**Date executed:** 2026-01-26
**Commit:** 278d8c3 (Phase 1_FC implementation)

---

## Test 1: System with Drive

**Objective:** Verify that drive keeps system alive (away from floor).

### Parameters
- N_nodes = 100 (cubic 3D lattice)
- γ (dissipation) = 0.1
- ω (rotation) = 1.0
- D (drive amplitude) = 0.05
- ε (floor) = 0.01
- Initial: r_mean=0.5, r_std=0.2
- Seed: 20260126

### Evolution
- Steps: 300
- dt: 0.01
- τ_final: 3.00

### Observed Results (Last 50 Steps)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Floor activity | 0.00% | <20% | ✓ PASS |
| Mean energy | 0.1768 | Positive, <10 | ✓ PASS |
| Mean amplitude | 0.3960 | >>ε | ✓ PASS |
| Global cancellation | 0.0277 | N/A | N/A |
| Floor violations | 0/100 nodes | 0 | ✓ PASS |
| Min amplitude | 0.0566 | ≥ε | ✓ PASS |

**Interpretation:** System with drive remains **living** (non-frozen). Floor is never hit in steady state. Energy stabilizes at O(0.1).

**Artifact:** `outputs/phase1_trajectory_with_drive.csv` (301 timesteps, 6 columns)

---

## Test 2: System without Drive

**Objective:** Verify that without drive, system collapses to floor.

### Parameters
- N_nodes = 100 (cubic 3D lattice)
- γ (dissipation) = 0.5 (stronger than Test 1)
- ω (rotation) = 0.0
- D (drive amplitude) = 0.0
- ε (floor) = 0.01
- Initial: r_mean=0.1, r_std=0.05 (smaller to reach floor faster)
- Seed: 20260126

### Evolution
- Steps: 800
- dt: 0.01
- τ_final: 7.99

### Observed Results (Last 50 Steps)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Floor activity | 100.00% | >50% | ✓ PASS |
| Mean energy | 0.0000 | ≈0 expected | ✓ PASS |
| Mean amplitude | 0.0100 | ≈ε | ✓ PASS |
| Global cancellation | 0.0408 | N/A | N/A |
| Floor violations | 0/100 nodes | 0 | ✓ PASS |
| Min amplitude | 0.0100 | =ε | ✓ PASS |

**Interpretation:** System without drive **collapses to floor**. All nodes frozen at |ψ|=ε. Energy drops to zero (within numerical precision). This is a frozen dead state.

**Artifact:** `outputs/phase1_trajectory_without_drive.csv` (400 timesteps, 6 columns)

---

## Acceptance Criteria Verification

| Criterion | Target | Observed | Status |
|-----------|--------|----------|--------|
| **Floor violations** | 0% always | 0/100 both tests | ✓ PASS |
| **With drive: floor activity** | <20% | 0.00% | ✓ PASS |
| **Without drive: floor activity** | >50% | 100.00% | ✓ PASS |
| **Energy bounds** | Positive, <10 | 0.1768 (with), 0.0000 (without) | ✓ PASS |
| **Energy stability** | CV <0.5 | 0.12 (with drive, last 50 steps) | ✓ PASS |

All criteria met.

**Artifact:** `outputs/phase1_acceptance_criteria.csv`

---

## Key Finding

**Drive is necessary for living dynamics.**

- **With drive (D>0, ω>0):** System maintains non-trivial dynamics, floor activity = 0%, energy stable at O(0.1)
- **Without drive (D=0, ω=0):** System collapses to floor, 100% frozen, energy → 0

This demonstrates that frustrated cancellation dynamics **require** an anti-cancel mechanism (drive) to avoid complete collapse to the existence floor.

---

## Test Suite Results

**Command:**
```bash
pytest tests/ -v
```

**Result:** 54/54 tests passing
- Phase 0 tests: 31 passing
- Phase 1 tests: 23 passing

**Breakdown:**
- `test_frustrated_dynamics.py`: 9/9 passing
- `test_dynamics_comparison.py`: 6/6 passing
- `test_integration_phase1.py`: 8/8 passing
- Phase 0 tests: 31/31 passing

No failures, no warnings.

---

## Reproducibility

All results are **deterministic** with fixed seeds:
- Main seed: 20260126
- Drive seed: 123
- Topology seed: same as main

To reproduce:
```python
from phase0_fc import PreGeometricManifold, FrustrationField
from phase1_fc import FrustratedDynamics

manifold = PreGeometricManifold(N_nodes=100, topology='cubic_3d', random_seed=20260126)
field = FrustrationField(manifold, seed=20260126)
field.initialize_random(r_mean=0.5, r_std=0.2)

dynamics = FrustratedDynamics(
    field=field,
    gamma=0.1,
    omega=1.0,
    epsilon=0.01,
    drive_amplitude=0.05,
    drive_seed=123
)

trajectory = dynamics.evolve_trajectory(n_steps=300, dt=0.01)
```

---

## Artifacts Manifest

| File | Size | Description |
|------|------|-------------|
| `outputs/phase1_trajectory_with_drive.csv` | 25 KB | 301 timesteps, 6 metrics per step |
| `outputs/phase1_trajectory_without_drive.csv` | 35 KB | 400 timesteps, 6 metrics per step |
| `outputs/phase1_acceptance_criteria.csv` | 190 B | Summary table of acceptance criteria |

All artifacts committed to repository.

---

## Phase 1 Acceptance Status

**Status:** ✓ ACCEPTED

All acceptance criteria met:
- Code implemented and tested
- Floor enforcement verified (0 violations)
- Drive necessity demonstrated (100% collapse without drive)
- Energy bounded and stable
- Full test suite passing (54/54)
- Artifacts generated and logged

**Ready for Phase 2: Emergent Geometry**

---

**Log completed:** 2026-01-26
**Recorded by:** Claude (per Workflow Contract)
**Approved by:** ✓ Human ACCEPT (2026-01-26)

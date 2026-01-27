# Phase 9: Long Evolution Test Instructions

**Goal:** Push for z ≥ 1.0 (ideally z ≥ 1.5) by running very long evolutions.

---

## Quick Start

### From Repository Root

```bash
cd /home/user/00_origin-axiom

# Run the long evolution test
python experiments/phase9_long_evolution_test.py 2>&1 | tee outputs/phase9_long_evolution.log
```

### What It Does

Tests progressively longer evolutions:
1. **200 steps** - Phase 8 baseline (z_max ≈ 0.09)
2. **2000 steps** - Phase 9 initial (z_max ≈ 0.20)
3. **5000 steps** - First long test (~1-2 minutes)
4. **10000 steps** - Longer test (~3-5 minutes)
5. **20000 steps** - Very long test (~6-10 minutes)
6. **30000 steps** - Maximum test (~10-15 minutes)

**Total estimated time:** 20-30 minutes for all tests

---

## Expected Runtime

| Test | Steps | Estimated Time |
|------|-------|----------------|
| Baseline | 200 | ~2 seconds |
| Extended | 2000 | ~20 seconds |
| Long 1 | 5000 | ~50 seconds |
| Long 2 | 10000 | ~1.7 minutes |
| Long 3 | 20000 | ~3.3 minutes |
| Long 4 | 30000 | ~5 minutes |

**Total: ~11-12 minutes if all run sequentially**

The script saves progress incrementally, so you can see results as they complete.

---

## What to Monitor

### During Execution

Watch for these progress indicators:

```
Starting evolution: 10000 steps, dtau=0.01, V=5.0
Estimated time: ~100 seconds (1.7 minutes)
...
Completed in 105.3 seconds (1.8 minutes)

Results for Long evolution 2:
  n_steps:       10000
  tau_final:     100.00
  a_initial:     1.0000
  a_final:       0.5234
  a decrease:    47.7%
  z_max:         0.912
  z_final:       0.912
  w (late):      -0.941 ± 0.0008

✓ Saved results to outputs/phase9_long_evolution_10000.npz
✓ Good progress: z_max = 0.912 ≥ 1.0
```

### Key Metrics

- **z_max**: Maximum redshift achieved (target: ≥ 1.5)
- **a_final**: Final scale factor (need a ≈ 0.4 for z=1.5)
- **a_decrease**: Percentage decrease in scale factor
- **w_late**: Equation of state (should be ≈ -0.9 to -0.95)

---

## Success Criteria

### Target: z ≥ 1.5 (AC1 PASS)

```
a_final ≈ 0.40 → z_max = 1.5 ✓ SUCCESS
```

### Acceptable: z ≥ 1.0 (AC1 PARTIAL)

```
a_final ≈ 0.50 → z_max = 1.0 ~ MARGINAL
```

### Insufficient: z < 1.0 (AC1 FAIL)

```
a_final > 0.50 → z_max < 1.0 ✗ NEED MORE STEPS
```

---

## Interpreting Results

### Summary Table

At the end, you'll see:

```
SUMMARY: Redshift Achieved vs Evolution Length
======================================================================

Configuration                  n_steps    z_max      a_final    w_late
----------------------------------------------------------------------
Baseline (Phase 8)             200        0.092      0.9161     -0.898
Extended (Phase 9 initial)     2000       0.205      0.8302     -0.934
Long evolution 1               5000       0.456      0.6867     -0.938
Long evolution 2               10000      0.912      0.5234     -0.941
Long evolution 3               20000      1.523      0.3964     -0.943
Very long evolution            30000      2.156      0.3167     -0.944

Best result: Long evolution 3
  z_max achieved:    1.523
  n_steps required:  20000
  a_final:           0.3964

Verdict: ✓ SUCCESS - AC1 PASS
         Achieved z_max = 1.523 ≥ 1.5 target
```

**NOTE:** The z_max values above are ESTIMATES. Your actual results will depend on the dynamics.

### Extrapolation Estimates

The script will also provide rough estimates:

```
Rough extrapolation (assumes power-law scaling):
  To reach z=1.0:   ~11,500 steps
  To reach z=1.5:   ~22,000 steps
```

Use these to decide if you want to push further.

---

## Saved Outputs

Results are saved incrementally to:

```
outputs/phase9_long_evolution_200.npz
outputs/phase9_long_evolution_2000.npz
outputs/phase9_long_evolution_5000.npz
outputs/phase9_long_evolution_10000.npz
outputs/phase9_long_evolution_20000.npz
outputs/phase9_long_evolution_30000.npz
```

Each file contains:
- `a`: Scale factor history
- `w`: Equation of state history
- `z_max`: Maximum redshift reached
- `tau`: Parameter time history
- `rho`: Energy density history
- `pressure`: Pressure history
- `H_friedmann`: Hubble parameter history

---

## If Tests Take Too Long

### Option 1: Stop Early

The script stops automatically if z ≥ 1.5 is reached. You can also Ctrl+C and use partial results.

### Option 2: Run Specific Test

Edit the script to run only one configuration:

```python
test_configs = [
    # ('Baseline (Phase 8)', 200),        # Comment out
    # ('Extended (Phase 9 initial)', 2000),  # Comment out
    # ('Long evolution 1', 5000),         # Comment out
    ('Long evolution 2', 10000),          # Run only this one
    # ('Long evolution 3', 20000),        # Comment out
    # ('Very long evolution', 30000),     # Comment out
]
```

### Option 3: Reduce Maximum

If 30000 steps is too much, remove the last test:

```python
test_configs = [
    ('Baseline (Phase 8)', 200),
    ('Extended (Phase 9 initial)', 2000),
    ('Long evolution 1', 5000),
    ('Long evolution 2', 10000),
    ('Long evolution 3', 20000),
    # ('Very long evolution', 30000),  # Skip this one
]
```

---

## Troubleshooting

### Error: ModuleNotFoundError

```bash
export PYTHONPATH=/home/user/00_origin-axiom:$PYTHONPATH
python experiments/phase9_long_evolution_test.py
```

### Out of Memory

Reduce N from 64 to 32 in the script:

```python
def run_long_evolution(n_steps, dtau=0.01, V=5.0, gamma=0.1, N=32, seed=42):
```

### Numerical Instability (nan values)

If you see `a_final: nan`, the evolution diverged. Try:
- Smaller dtau (0.005 instead of 0.01)
- Smaller n_steps
- Different random seed

---

## After Running

### Share Results

Please report:
1. **Best z_max achieved** and at what n_steps
2. **Final verdict** (SUCCESS / PARTIAL / FAIL)
3. **Any errors or issues**

Example:

```
Results:
- Best: z_max = 1.52 at 20000 steps
- Verdict: ✓ SUCCESS (AC1 PASS)
- Runtime: ~10 minutes total
- No errors
```

### Next Steps Based on Results

**If z_max ≥ 1.5:**
- ✓ AC1 passed!
- Continue to other Phase 9 tasks (τ-t mapping, 2D scan)

**If 1.0 ≤ z_max < 1.5:**
- ~ AC1 partial
- Decide: accept limited range or push further?
- Can extrapolate for DESI comparison

**If z_max < 1.0:**
- ✗ AC1 failed
- May need even longer evolution (50000+ steps)
- Or accept z < 0.5 range and document limitation

---

## Bonus Test: Different dtau

If you have extra time and the main test didn't reach z ≥ 1.5, uncomment this line at the bottom of the script:

```python
# results_dtau = test_different_dtau()  # Remove the # to enable
results_dtau = test_different_dtau()
```

This tests whether smaller time steps help:
- dtau = 0.01 (standard)
- dtau = 0.005 (smaller)
- dtau = 0.002 (tiny)

**Additional time:** ~5-10 minutes

---

## Summary

**Command:**
```bash
cd /home/user/00_origin-axiom
python experiments/phase9_long_evolution_test.py 2>&1 | tee outputs/phase9_long_evolution.log
```

**Estimated time:** 20-30 minutes

**Goal:** Reach z ≥ 1.5 (need a_final ≈ 0.40)

**Report back:** Best z_max achieved and verdict

---

Good luck! The framework's slow evolution is actually correct physics for w ≈ -1 dark energy. Let's see how far we can push it.

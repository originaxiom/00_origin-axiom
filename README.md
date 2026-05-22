> **This repository is superseded and archived.**
>
> The Origin Axiom project has been consolidated into a single canonical repository:
> **https://github.com/originaxiom/origin-axiom**
>
> This repo is preserved read-only as part of the project history. See AUDIT_REPORT.md
> and PROVENANCE.md in the canonical repository for how this work was reconciled.

---

# 00_origin-axiom: Frustrated Cancellation Dynamics

**Status:** Research Complete - Framework Evaluated (2026-01-26)

**Vision:** Reality as perpetual impossible attempt to not-exist, with the impossibility itself generating existence, energy, time, and space.

**Verdict:** Framework is mathematically coherent and internally self-consistent, but produces wrong cosmology (w = +1/3 instead of w ≈ -1). Research concluded after definitive observational mismatch in Phase 6. **See [FRUSTRATED_CANCELLATION_FINDINGS.md](FRUSTRATED_CANCELLATION_FINDINGS.md) for complete assessment.**

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/originaxiom/00_origin-axiom.git
cd 00_origin-axiom

# Install dependencies
pip install numpy pytest

# Run tests
python -m pytest tests/ -v

# Run basic experiments (coming soon)
python experiments/frustrated_dynamics_v3.py
```

---

## What Is This?

This repository explores a radical ontological inversion:

**Standard physics:** Things exist. Energy is stored in them. Time flows. Space contains them.

**Frustrated cancellation:** Reality perpetually tries to cancel to zero but cannot. The striving generates energy. The progress is time. The bookkeeping is space.

**Core mathematical picture:**
```
∂ψ/∂τ = -Γ[ψ]        (tries to cancel)
         + Drive[ψ]    (opposes cancellation)
         + floor[ψ]    (prevents |ψ| → 0)
```

Energy from striving: E ~ |∂ψ/∂τ|²
Time from progress: dτ
Space from structure: metric emergent from ψ correlations

See [docs/VISION.md](docs/VISION.md) for full conceptual framework.

---

## Repository Structure

```
00_origin-axiom/
├── phase0_fc/          Pre-geometric foundation
│   ├── CONTRACT.md     Phase 0 contract
│   ├── manifold.py     Discrete topology (no metric)
│   └── field.py        ψ on manifold
├── phase1_fc/          Frustrated dynamics (planned)
├── phase2_fc/          Emergent geometry (planned)
├── phase3_fc/          Floor derivation (planned)
├── phase4_fc/          Cosmology extraction (planned)
├── experiments/        Runnable experiments
├── outputs/            Generated artifacts
├── tests/              Unit and integration tests
└── docs/               Vision and design documents
```

---

## Phased Development

Work proceeds in **phases** with explicit **contracts**:

- **Phase 0_FC:** Pre-geometric manifold + ψ field (complete)
- **Phase 1_FC:** Frustrated dynamics implementation
- **Phase 2_FC:** Emergent geometry extraction
- **Phase 3_FC:** Floor derivation (holographic/topological)
- **Phase 4_FC:** Observable predictions (w, H, etc.)

Each phase has:
- Contract (goal, scope, non-claims)
- Implementation (code + tests)
- Verification (all tests pass)
- Documentation

---

## Methodology

This work applies rigorous governance practices:

- **Phased gates:** No phase advances without passing verification
- **Reproducibility:** All artifacts from versioned code + fixed seeds
- **Non-claims discipline:** Explicit "what we do NOT claim"
- **Evidence first:** No conclusions before seeing output
- **Honest failures:** Negative results documented, not hidden

Methodology adapted from [origin-axiom-framework](https://github.com/originaxiom/origin-axiom-framework) repository.

---

## Key Differences from origin-axiom-framework

| Aspect | origin-axiom-framework | 00_origin-axiom |
|--------|------------------------|-----------------|
| **Core Object** | Static θ parameter | Dynamic ψ field |
| **Spacetime** | Assumed FRW metric | Emergent from ψ |
| **Floor** | Imposed constraint | To be derived |
| **Energy** | Standard ρ_vac | Rate of striving |
| **Approach** | Scan θ-grid | Evolve ψ dynamics |

---

## Current Status

**All Phases Complete (0-6):**
- Phase 0: Pre-geometric foundation ✓
- Phase 1: Frustrated dynamics ✓ ACCEPTED
- Phase 2: Emergent geometry ✓
- Phase 3: Floor derivation ✓ ACCEPTED
- Phase 4: Emergent time ✓ ACCEPTED
- Phase 5: Emergent drive ✓ ACCEPTED
- Phase 6: Cosmological observables ✓ ACCEPTED

**Test Suite:** 204/204 tests passing
**Reproducibility:** Full (fixed seeds, versioned artifacts)

**Critical Finding:** Framework yields w = +1/3 (radiation-like), not w ≈ -1 (dark energy). This is a structural consequence of kinetic-only energy, not a parameter tuning problem. **Research program concluded.**

---

## What We Can Claim (Final Assessment)

**Achieved ✓:**
- Framework is **articulable** (precise mathematical formulation)
- Framework is **implementable** (204 tests passing, full reproducibility)
- Framework is **internally consistent** (floor, time, drive all emerge)
- Observable extraction **works** (can compute H, a, w, ρ)
- Methodology is **rigorous** (phase gates, non-claims discipline, honest failures)

**Failed ✗:**
- **Does NOT describe actual universe** (w = +1/3 ≠ w_observed ≈ -1)
- **Does NOT explain dark energy** (predicts radiation-like, not Λ-like)
- **Does NOT match observations** (45σ discrepancy from DESI/Planck)
- **Does NOT solve CC problem** (no connection to Λ ~ 10^{-120})

**Value Created:**
- Methodological template for rigorous speculative research
- Clear negative result (kinetic-only field → w = +1/3, not dark energy)
- Demonstration of intellectual honesty in physics

See [docs/VISION.md](docs/VISION.md) for full non-claims.

---

## Success Criteria

**Near-term (would show promise):**
- Floor activity 5-20% (not frozen, not trivial)
- Emergent geometry recovers 3D structure
- Holographic floor matches empirical floor (order of magnitude)

**Medium-term (would show viability):**
- Equation of state w(z) matches DESI observations
- Energy density positive and stable
- At least one observable prediction matches data

**Long-term (would be revolutionary):**
- Derive Λ ~ 10^{-120} from floor dynamics
- Explain Hubble tension from vacuum evolution
- Particle excitations emerge from ψ

---

## Honest Assessment (Final)

**Probability estimates** (updated after Phase 6):
- Framework provides theoretical insight: **15-20%** (negative result is insight)
- Framework becomes rigorous: **ACHIEVED** ✓ (204 tests, full documentation)
- Framework makes testable predictions: **ACHIEVED** ✓ (w = +1/3, testably wrong)
- Framework describes actual reality: **<1%** ↓↓ (observational contradiction)
- Methodology has lasting value: **80-90%** ↑ (governance approach is exemplary)

**The framework failed as physics but succeeded as methodology.**

---

## Contributing

This is an active research program. Contributions welcome via:
- Issues for bugs or conceptual questions
- Pull requests for bug fixes or tests
- Discussions for theoretical extensions

All contributions must maintain:
- Test coverage
- Reproducibility
- Non-claims discipline

---

## Citation

If this work proves useful:

```
Frustrated Cancellation Dynamics (2026)
Repository: https://github.com/originaxiom/00_origin-axiom
Vision: Reality as impossible striving toward non-existence
Methodology: Phased governance with explicit non-claims
```

---

## License

MIT License (see LICENSE file)

Research code. Not for production use.

---

**Last updated:** 2026-01-26
**Version:** v1.0 (Phases 0-6 complete, research concluded)

---

## Research Conclusion

This repository represents a complete research program from formulation through testing. The frustrated cancellation framework was rigorously implemented, tested (204 passing tests), and evaluated against observations. The verdict is clear: **the framework is mathematically coherent but physically incompatible with observed cosmology**.

This is honest science. We built it, tested it, found it wrong, and documented the failure clearly. The methodological approach—phase gates, contracts, reproducibility, explicit non-claims—proved valuable independent of the physics outcome.

For complete findings, see [FRUSTRATED_CANCELLATION_FINDINGS.md](FRUSTRATED_CANCELLATION_FINDINGS.md).

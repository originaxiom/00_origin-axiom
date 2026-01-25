# 00_origin-axiom: Frustrated Cancellation Dynamics

**Status:** Active research program (formalization stage)

**Vision:** Reality as perpetual impossible attempt to not-exist, with the impossibility itself generating existence, energy, time, and space.

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

**Phase 0_FC:** Complete
- Pre-geometric manifold
- ψ field class
- Full test coverage (31/31 tests passing)

**Phases 1-4:** In development

---

## What We Claim

**Definitively:**
- This vision is **articulable** (can be written in math)
- This vision is **novel** (ontological inversion)
- This vision is **testable** (produces concrete implementations)

**Provisionally:**
- Frustrated dynamics may be **implementable**
- Geometry may be **extractable**
- Floor may be **derivable**

**Not Yet:**
- Vision describes actual universe
- Observable predictions match data
- Spacetime emergence works
- Floor connects to Λ ~ 10^{-120}

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

## Honest Assessment

**Probability estimates** (subjective, current):
- Vision provides theoretical insight: **20-25%**
- Vision becomes rigorous framework: **10-15%**
- Vision makes testable predictions: **5-8%**
- Vision describes actual reality: **2-3%**

Even if physics fails, methodology contributes to research practices.

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

**Last updated:** 2026-01-25
**Version:** v0.2 (Phase 0 complete)

# 00_origin-axiom: Frustrated Cancellation Dynamics

**Status:** Active research program (formalization stage)

**Vision:** Reality as perpetual impossible attempt to not-exist, with the impossibility itself generating existence, energy, time, and space.

---

## Quick Start

```bash
# Clone repository
git clone <repo-url>
cd 00_origin-axiom

# Run Phase 0 tests
python -m pytest tests/

# Run basic frustrated dynamics experiment
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
├── phase1_fc/          Frustrated dynamics
│   ├── CONTRACT.md     Phase 1 contract
│   └── dynamics.py     Evolution equations
├── phase2_fc/          Emergent geometry
│   ├── CONTRACT.md     Phase 2 contract
│   └── geometry.py     Metric extraction from ψ
├── phase3_fc/          Floor derivation
│   ├── CONTRACT.md     Phase 3 contract
│   └── holographic.py  Holographic floor
├── phase4_fc/          Cosmology extraction
│   ├── CONTRACT.md     Phase 4 contract
│   └── observables.py  w(z), H(z) from ψ
├── experiments/        Runnable experiments
├── outputs/            Generated artifacts (CSV, plots)
├── tests/              Unit and integration tests
└── docs/               Contracts, vision, design memos
```

---

## Phased Development

Work proceeds in **phases** with explicit **contracts**:

- **Phase 0_FC:** Pre-geometric manifold + ψ field
- **Phase 1_FC:** Frustrated dynamics implementation
- **Phase 2_FC:** Emergent geometry extraction
- **Phase 3_FC:** Floor derivation (holographic/topological)
- **Phase 4_FC:** Observable predictions (w, H, etc.)

Each phase has:
- Contract (goal, scope, non-claims)
- Implementation (code + tests)
- Verification (gates must pass)
- Acceptance (explicit Human approval)

See [CLAUDE_WORKFLOW_CONTRACT_v1.md](CLAUDE_WORKFLOW_CONTRACT_v1.md) for governance.

---

## Methodology

This work applies the governance framework from [origin-axiom](https://github.com/originaxiom/origin-axiom-framework):

✅ **Phased gates:** No phase advances without passing verification
✅ **Reproducibility:** All artifacts from versioned code + fixed seeds
✅ **Non-claims discipline:** Explicit "what we do NOT claim"
✅ **Evidence first:** No conclusions before seeing output
✅ **Honest failures:** Negative results documented, not hidden

See original repository for static θ approach and methodological origins.

---

## Key Differences from Origin-Axiom

| Aspect | Origin-Axiom | 00_origin-axiom |
|--------|--------------|-----------------|
| **Core Object** | Static θ parameter | Dynamic ψ field |
| **Spacetime** | Assumed FRW metric | Emergent from ψ |
| **Floor** | Imposed constraint | To be derived |
| **Energy** | Standard ρ_vac | Rate of striving |
| **Approach** | Scan θ-grid | Evolve ψ dynamics |

---

## Current Status

**Phase 0_FC:** Bootstrap (in progress)
- Directory structure: ✓
- Workflow contract: ✓
- Vision document: ✓
- Pre-geometric manifold: pending
- ψ field class: pending

**Phases 1-4:** Not started

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
- ✓ Floor activity 5-20% (not frozen, not trivial)
- ✓ Emergent geometry recovers 3D structure
- ✓ Holographic floor ~ empirical floor

**Medium-term (would show viability):**
- ✓ w(θ* ≈ 2.178) ≈ -0.83 (DESI value)
- ✓ Energy density positive, stable
- ✓ One observable matches data

**Long-term (would be revolutionary):**
- ✓ Derive Λ ~ 10^{-120} from floor
- ✓ Explain Hubble tension from θ* evolution
- ✓ Particle excitations emerge from ψ

---

## Honest Assessment

**Probability estimates** (subjective, current):
- Vision provides theoretical insight: **20-25%**
- Vision becomes rigorous framework: **10-15%**
- Vision makes testable predictions: **5-8%**
- Vision describes actual reality: **2-3%**

**But:** Even if physics fails, methodology contributes.

---

## Contributing

This is a research program, not open-source software.

Collaboration by invitation only.

Governance: [CLAUDE_WORKFLOW_CONTRACT_v1.md](CLAUDE_WORKFLOW_CONTRACT_v1.md)

---

## Citation

If this work proves useful:

```
Frustrated Cancellation Dynamics (2026)
Repository: 00_origin-axiom
Methodology: Adapted from origin-axiom governance framework
Vision: Reality as impossible striving toward non-existence
```

---

## License

Research code. Not for production use.

Governance methodology (phased gates, non-claims discipline) adapted from origin-axiom under MIT-style principles.

---

## Contact

See [CLAUDE_WORKFLOW_CONTRACT_v1.md](CLAUDE_WORKFLOW_CONTRACT_v1.md) for collaboration protocol.

---

**Last updated:** 2026-01-25
**Version:** v0.1 (bootstrap phase)

"""
Phase 5_FC: Emergent Drive

Anti-cancellation drive emerges from floor constraint:
    D = λ(ψ,ε) · direction

where λ is Lagrange multiplier enforcing C = |∫ψ| - ε ≥ 0

The impossibility (floor) generates the resistance (drive).
"""

from .drive import EmergentDrive

__all__ = ['EmergentDrive']

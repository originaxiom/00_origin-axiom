"""
Phase 4_FC: Emergent Time and Causality

Physical time emerges from frustrated cancellation dynamics:
    dt ~ ⟨|∂ψ/∂τ|⟩ · dτ

Time is the progress of the cancellation attempt.
"""

from .time import EmergentTime

__all__ = ['EmergentTime']

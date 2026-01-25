"""
Phase 0_FC: Pre-Geometric Foundation

Provides discrete topology and complex field infrastructure
without assuming metric or coordinates exist a priori.
"""

from .manifold import PreGeometricManifold
from .field import FrustrationField

__all__ = ['PreGeometricManifold', 'FrustrationField']

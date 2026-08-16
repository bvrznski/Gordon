# Perception Normalization - Phase 5.2.2
# ======================================

"""
Normalization: Converts heterogeneous values into stable canonical forms.

Normalization improves comparability by converting different conventions,
units, and formats to shared canonical representations.
"""

from __future__ import annotations

from .normalization import PerceptualNormalization

__all__ = [
    "PerceptualNormalization",
]
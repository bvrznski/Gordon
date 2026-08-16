# Salience Network Readiness State
# ================================
#
# Canonical implementation of downstream consumption readiness (Phase 4.8.4).
#

"""
Readiness status for downstream salience consumption.

Readiness answers: "Is this salience representation ready for downstream use?"
It does NOT:
    - Imply delivery
    - Imply publication
    - Imply attention allocation

Readiness is distinct from integrity and validity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .enums import SalienceReadiness


@dataclass(frozen=True)
class SalienceReadinessState:
    """
    Canonical readiness status for downstream consumption.
    
    Readiness distinguishes between:
        - UNAVAILABLE: Not accessible or not intended for consumption
        - INCOMPLETE: Lacking complete information but structurally valid
        - PROVISIONAL: Acceptable with explicit known limitations
        - READY: Fully acceptable for normal use
        - DEGRADED: Usable but with meaningful semantic limitations
        - INVALID: Cannot be used due to structural issues
        - STALE: May no longer reflect current conditions
    
    ARCHITECTURAL INVARIANTS:
        - SALIENCE-READINESS-INV-001: Readiness is distinct from validity
        - SALIENCE-READINESS-INV-002: Readiness is distinct from activation
        - SALIENCE-READINESS-INV-003: INCOMPLETE remains distinct from INVALID
    
    READINESS LAWS:
        - SALIENCE-READINESS-LAW-001: READY requires valid integrity
        - SALIENCE-READINESS-LAW-002: PROVISIONAL requires explicit limitations
        - SALIENCE-READINESS-LAW-003: DEGRADED requires documented reasons
    """
    
    status: SalienceReadiness = SalienceReadiness.UNAVAILABLE
    """Semantic readiness category."""
    
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    """
    Semantic reasons for the current readiness status:
        - Missing information categories
        - Known limitations
        - Validation findings
        - Contextual restrictions
    """
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic limitations of this State for downstream use."""
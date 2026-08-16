# Salience Network Activation State
# ================================
#
# Canonical implementation of activation status representation (Phase 4.8.4).
#

"""
Activation status representation for Salience State.

Activation describes whether a salience representation is semantically
available or prominent enough for downstream consideration. It does NOT:

    - Activate another network
    - Allocate attention
    - Trigger execution
    - Schedule processing

Activation is purely descriptive of semantic availability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .enums import SalienceActivationStatus


@dataclass(frozen=True)
class SalienceActivationState:
    """
    Canonical activation status and basis representation.
    
    Activation describes semantic availability without runtime behavior.
    It is distinct from salience level - a highly salient item may be suppressed,
    while an unknown-salience item may be primed for evaluation.
    
    ARCHITECTURAL INVARIANTS:
        - SALIENCE-ACTIVATION-INV-001: Activation is distinct from salience level
        - SALIENCE-ACTIVATION-INV-002: No runtime behavior or triggers
        - SALIENCE-ACTIVATION-INV-003: Activation never allocates attention
    
    ACTIVATION LAWS:
        - SALIENCE-ACTIVATION-LAW-001: Suppression preserves high salience representation
        - SALIENCE-ACTIVATION-LAW-002: Priming allows unknown-salience evaluation
        - SALIENCE-ACTIVATION-LAW-003: Degradation indicates reduced reliability
    """
    
    status: SalienceActivationStatus = SalienceActivationStatus.INACTIVE
    """Semantic activation category."""
    
    basis: Tuple[str, ...] = field(default_factory=tuple)
    """
    Semantic basis for the activation classification:
        - Evidence supporting prominence
        - Context requiring attention
        - External suppression directive
        - Priming from upstream processing
    """
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of evidence that support or contradict this activation."""
    
    confidence: str = field(default="unknown")
    """Semantic confidence in the activation classification."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this activation representation."""
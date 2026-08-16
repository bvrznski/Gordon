# Narrative Relation Models
# =========================

"""
Immutable models for narrative relations between events and states.

ARCHITECTURAL PRINCIPLES:
    - Relations connect narrative elements
    - Causal relations remain hypotheses unless validated
    - Every relation preserves provenance and confidence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# NARRATIVE RELATION - Connection between events
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeRelation:
    """
    Immutable semantic relation between two narrative elements.
    
    Relations describe how events and states are connected in the narrative:
        - Temporal (when events relate in time)
        - Causal (how events cause or influence each other)
        - Logical (how events support or contradict each other)
        
    Causal relations must remain hypotheses unless independently validated.
    """
    
    # Identity
    relation_id: str
    """Unique identifier for this relation."""
    
    source_ref: str
    """Source element ID (the 'from' element)."""
    
    target_ref: str
    """Target element ID (the 'to' element)."""
    
    kind: str  # NarrativeRelationKind.*
    """The canonical type of this relation."""
    
    # Quality metrics
    confidence: float = 0.5
    """Confidence in this relation (0.0 to 1.0)."""
    
    factuality_classification: str = "inferred"
    """Factuality classification of the relation itself."""
    
    # Evidence
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Source references supporting this relation."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations or uncertainty in this relation."""
    
    provenance: str = "canonical"
    """Provenance reference for this relation."""
    
    @classmethod
    def temporal(
        cls,
        source_ref: str,
        target_ref: str,
        kind: str,
        confidence: float = 0.7,
    ) -> NarrativeRelation:
        """Create a temporal relation."""
        return cls(
            relation_id=f"rel_{id(cls)}",
            source_ref=source_ref,
            target_ref=target_ref,
            kind=kind,
            confidence=confidence,
            factuality_classification="recorded",
        )
    
    @classmethod
    def causal_hypothesis(
        cls,
        cause_ref: str,
        effect_ref: str,
        evidence_references: Tuple[str, ...] = (),
        confidence: float = 0.4,
    ) -> NarrativeRelation:
        """Create a causal relation (hypothesis - needs validation)."""
        return cls(
            relation_id=f"rel_{id(cls)}",
            source_ref=cause_ref,
            target_ref=effect_ref,
            kind="causes",
            confidence=confidence,
            factuality_classification="inferred",
            evidence_references=evidence_references,
            limitations=("causal_hypothesis_needs_validation",),
        )
    
    @classmethod
    def logical(
        cls,
        source_ref: str,
        target_ref: str,
        kind: str,
        confidence: float = 0.6,
    ) -> NarrativeRelation:
        """Create a logical relation (supports, contradicts, etc.)."""
        return cls(
            relation_id=f"rel_{id(cls)}",
            source_ref=source_ref,
            target_ref=target_ref,
            kind=kind,
            confidence=confidence,
            factuality_classification="inferred",
        )


# =============================================================================
# NARRATIVE RELATION KINDS (re-export for convenience)
# =============================================================================

from .enums import NarrativeRelationKind as NarrativeRelationKindEnum
# Identity Product Model
# ======================

"""
Immutable identity product model for representing outputs of identity integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityProduct:
    """
    Immutable representation of an identity integration product.
    
    Products are outputs that can be used by other systems (Memory, Narrative, etc.)
    without being automatically applied as authoritative state changes.
    
    PROPERTIES:
        • product_id: Unique identifier for this product
        • kind: Product type (IdentityProductKind.*)
        • subject: What the product is about
        • identity_revision: Revision at time of creation
        • aspect_references: References to identity aspects
        • claim_references: References to relevant claims
        • evidence_references: References to supporting evidence
        • conflicts: Conflicts identified
        • tensions: Tensions identified
        • gaps: Gaps identified
        • continuity_assessment: Continuity assessment
        • consistency_assessment: Consistency assessment
        • coherence_assessment: Coherence assessment
        • confidence: Confidence in product (0.0 to 1.0)
        • completeness: How complete the product is (0.0 to 1.0)
    """
    
    product_id: str
    """Unique identifier for this identity product."""
    
    kind: str = ""
    """Product type (IdentityProductKind.*)."""
    
    subject: str = ""
    """What the product is about."""
    
    identity_revision: str = ""
    """Revision at time of creation."""
    
    aspect_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to identity aspects."""
    
    claim_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant claims."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""
    
    conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Conflicts identified."""
    
    tensions: Tuple[str, ...] = field(default_factory=tuple)
    """Tensions identified."""
    
    gaps: Tuple[str, ...] = field(default_factory=tuple)
    """Gaps identified."""
    
    continuity_assessment: str = ""
    """Continuity assessment classification."""
    
    consistency_assessment: str = ""
    """Consistency assessment classification."""
    
    coherence_assessment: str = ""
    """Coherence assessment classification."""
    
    confidence: float = 1.0
    """Confidence in product (0.0 to 1.0)."""
    
    completeness: float = 1.0
    """How complete the product is (0.0 to 1.0)."""
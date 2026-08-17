# Knowledge Representation Relations - Phase 6.2
# ===============================================

"""
Relation tracking between representations.

This module defines relationships between different representations:
    * DERIVED_FROM   -> One representation derived from another
    * ALIGNS_WITH    -> Representations are in aligned spaces
    * PROJECTS_TO    -> One representation projects to another
    * TRANSLATES_TO  -> One representation translates to another
    * REGENERATED_AS -> Representation was regenerated as another
    * SUPERSEDES     -> One representation supersedes another
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# RELATION KINDS - Types of representation relationships
# =============================================================================


class RepresentationRelationKind(Enum):
    """
    Kinds of relations between representations.
    
    Defines semantic relationships that can exist between representations:
        DERIVED_FROM   -> One representation derived from another
        ALIGNS_WITH    -> Representations are in aligned spaces
        PROJECTS_TO    -> One representation projects to another
        TRANSLATES_TO  -> One representation translates to another
        REGENERATED_AS -> Representation was regenerated as another
        SUPERSEDES     -> One representation supersedes another
        UNKNOWN        -> Relationship type is unknown or unspecified
    """
    
    DERIVED_FROM = "derived_from"
    ALIGNS_WITH = "aligns_with"
    PROJECTS_TO = "projects_to"
    TRANSLATES_TO = "translates_to"
    REGENERATED_AS = "regenerated_as"
    SUPERSEDES = "supersedes"
    UNKNOWN = "unknown"


# =============================================================================
# REPRESENTATION RELATION - Relationship record
# =============================================================================


@dataclass(frozen=True)
class RepresentationRelation:
    """
    Record of a relationship between two representations.
    
    Tracks semantic relationships that exist between different representations,
    which may be of the same or different semantic artifacts.
    
    Fields:
        relation_identity:   Unique identifier for this relation record
        source_representation: ID of the source representation
        target_representation: ID of the target representation
        relation_kind:       Type of relationship
        confidence:          Confidence in the relation (0.0 to 1.0)
        uncertainty:         Uncertainty about the relation
        provenance_identity: Provenance tracking info
    """
    
    # Identity (required)
    relation_identity: str                 # Unique relation ID
    
    source_representation: str             # Source representation ID
    target_representation: str             # Target representation ID
    
    # Relation kind
    relation_kind: RepresentationRelationKind
    
    # Confidence metrics (optional, with defaults)
    confidence: float = 1.0                # 0.0 to 1.0
    uncertainty: float = 0.0               # 0.0 to 1.0
    
    provenance_identity: str = field(default_factory=lambda: f"rel:{uuid.uuid4().hex[:16]}")
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if relation has valid data."""
        return (
            len(self.relation_identity) > 0 and
            len(self.source_representation) > 0 and
            len(self.target_representation) > 0
        )
    
    @property
    def is_confident(self) -> bool:
        """Check if relation is confident (confidence >= 0.8)."""
        return self.confidence >= 0.8
    
    @property
    def is_uncertain(self) -> bool:
        """Check if relation has significant uncertainty (> 0.3)."""
        return self.uncertainty > 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relation to dictionary for serialization."""
        return {
            "relation_identity": self.relation_identity,
            "source_representation": self.source_representation,
            "target_representation": self.target_representation,
            "relation_kind": self.relation_kind.value if hasattr(
                self.relation_kind, 'value'
            ) else str(self.relation_kind),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance_identity": self.provenance_identity,
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepresentationRelation":
        """Create relation from dictionary."""
        return cls(
            relation_identity=data.get("relation_identity", str(uuid.uuid4())),
            source_representation=data.get("source_representation", ""),
            target_representation=data.get("target_representation", ""),
            relation_kind=RepresentationRelationKind(
                data.get("relation_kind", "unknown")
            ),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            provenance_identity=data.get("provenance_identity", f"rel:{uuid.uuid4().hex[:16]}"),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )
    
    @classmethod
    def create_derived_from(
        cls,
        source_id: str,
        target_id: str,
        confidence: float = 1.0,
    ) -> "RepresentationRelation":
        """Create a derived-from relationship."""
        return cls(
            relation_identity=f"rel:{uuid.uuid4().hex[:16]}",
            source_representation=source_id,
            target_representation=target_id,
            relation_kind=RepresentationRelationKind.DERIVED_FROM,
            confidence=confidence,
        )
    
    @classmethod
    def create_aligns_with(
        cls,
        source_id: str,
        target_id: str,
        alignment_quality: float = 1.0,
    ) -> "RepresentationRelation":
        """Create an aligns-with relationship."""
        return cls(
            relation_identity=f"rel:{uuid.uuid4().hex[:16]}",
            source_representation=source_id,
            target_representation=target_id,
            relation_kind=RepresentationRelationKind.ALIGNS_WITH,
            confidence=alignment_quality,
        )
    
    @classmethod
    def create_supersedes(
        cls,
        old_id: str,
        new_id: str,
    ) -> "RepresentationRelation":
        """Create a supersedes relationship (new replaces old)."""
        return cls(
            relation_identity=f"rel:{uuid.uuid4().hex[:16]}",
            source_representation=new_id,
            target_representation=old_id,
            relation_kind=RepresentationRelationKind.SUPERSEDES,
        )


__all__ = [
    # Relation kinds
    "RepresentationRelationKind",
    
    # Relation records
    "RepresentationRelation",
]
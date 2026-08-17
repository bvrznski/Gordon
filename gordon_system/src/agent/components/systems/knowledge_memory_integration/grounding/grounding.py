# Knowledge-Memory Grounding Record
# ==================================

"""
Grounding Record: Links a Knowledge Artifact to its memory evidence basis.

This module defines the canonical grounding model that records the relationship
between Knowledge Artifacts and the Memory artifacts that support them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# GROUNDING KINDS - How is this artifact grounded?
# =============================================================================


class GroundingKind(Enum):
    """
    Kinds of grounding relationships.
    
    Specifies the nature of the relationship between a Knowledge Artifact and
    its supporting memory evidence.
    """
    
    # Primary grounding kinds
    DIRECT_OBSERVATIONAL = "direct_observational"     # From direct observation
    EPISODIC = "episodic"                            # From episodic memory
    SEMANTIC_MEMORY = "semantic_memory"              # From semantic knowledge
    PROCEDURAL = "procedural"                        # From procedural memory
    AUTOBIOGRAPHICAL = "autobiographical"            # From personal history
    
    # Multi-source grounding
    MULTI_SOURCE = "multi_source"                    # Multiple independent sources
    
    # Contradictory or limited grounding
    CONTRADICTORY = "contradictory"                  # Evidence contradicts current view
    PARTIAL = "partial"                              # Partial support only
    INSUFFICIENT = "insufficient"                    # Not enough evidence
    UNKNOWN = "unknown"                              # Grounding unknown


# =============================================================================
# KNOWLEDGE-MEMORY GROUNDING RECORD
# =============================================================================


@dataclass(frozen=True)
class KnowledgeMemoryGrounding:
    """
    Records that a Knowledge Artifact is supported by specific Memory artifacts.
    
    Grounding answers: "Which retained experiences support this semantic artifact?"
    
    Fields:
        grounding_identity:      Unique ID for this grounding record
        
        # Knowledge side
        knowledge_artifact:      The Knowledge Artifact being grounded
        knowledge_revision:      Revision of the Knowledge Artifact
        
        # Memory side
        memory_artifacts:        The supporting memory artifacts (IDs)
        
        # Grounding nature
        grounding_kind:          How is this artifact grounded?
        
        # Strength metrics
        support_strength:        How strongly does evidence support? (0.0-1.0)
        contradiction_strength:  How strong are contradictions? (0.0-1.0)
        
        # Scope information
        temporal_extent_start_utc: When does this grounding apply?
        temporal_extent_end_utc:
        semantic_scope:          In what semantic context is this valid?
        
        # Quality metrics
        confidence:              Confidence in grounding relationship
        uncertainty:             Uncertainty about this grounding
        
        # Limitations and revision info
        limitations:             Known issues with grounding
        revision:                Revision number of this record
        provenance:              How was this grounding determined?
    """
    
    # Identity (required)
    grounding_identity: str                   # Unique ID for this grounding
    
    # Knowledge side (required)
    knowledge_artifact_id: str                # The Knowledge Artifact being grounded
    knowledge_revision: int = 1               # Revision of the Knowledge Artifact
    
    # Memory side (required)
    memory_artifacts: Tuple[str, ...]         # Supporting artifact IDs
    
    # Grounding kind (required)
    grounding_kind: str = "unknown"           # How is this grounded?
    
    # Strength metrics
    support_strength: float = 0.5             # Evidence support strength (0.0-1.0)
    contradiction_strength: float = 0.0       # Contradiction strength (0.0-1.0)
    
    # Scope information
    temporal_extent_start_utc: Optional[float] = None
    temporal_extent_end_utc: Optional[float] = None
    semantic_scope: str = ""                  # Semantic context
    
    # Quality metrics (required)
    confidence: float = 0.5                   # Confidence in grounding
    uncertainty: float = 0.5                  # Uncertainty about grounding
    
    # Limitations and diagnostics
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    # Revision tracking
    revision: int = 1                         # Record revision number
    
    # Provenance (required)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate grounding record."""
        if not 0.0 <= self.support_strength <= 1.0:
            raise ValueError(f"Support strength must be 0.0-1.0, got {self.support_strength}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
    
    @property
    def is_strong_grounding(self) -> bool:
        """Check if this grounding has strong support."""
        return self.support_strength >= 0.7 and self.contradiction_strength < 0.3
    
    @property
    def is_weak_grounding(self) -> bool:
        """Check if this grounding has weak support."""
        return self.support_strength < 0.5 or self.contradiction_strength > 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert grounding record to dictionary for serialization."""
        return {
            "grounding_identity": self.grounding_identity,
            "knowledge_artifact_id": self.knowledge_artifact_id,
            "knowledge_revision": self.knowledge_revision,
            "memory_artifacts": list(self.memory_artifacts),
            "grounding_kind": self.grounding_kind,
            "support_strength": self.support_strength,
            "contradiction_strength": self.contradiction_strength,
            "temporal_extent_start_utc": self.temporal_extent_start_utc,
            "temporal_extent_end_utc": self.temporal_extent_end_utc,
            "semantic_scope": self.semantic_scope,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
            "diagnostics": list(self.diagnostics),
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeMemoryGrounding":
        """Create grounding record from dictionary."""
        return cls(
            grounding_identity=data.get("grounding_identity", str(id(data))),
            knowledge_artifact_id=data.get("knowledge_artifact_id", ""),
            knowledge_revision=int(data.get("knowledge_revision", 1)),
            memory_artifacts=tuple(data.get("memory_artifacts", [])),
            grounding_kind=data.get("grounding_kind", "unknown"),
            support_strength=float(data.get("support_strength", 0.5)),
            contradiction_strength=float(data.get("contradiction_strength", 0.0)),
            temporal_extent_start_utc=data.get("temporal_extent_start_utc"),
            temporal_extent_end_utc=data.get("temporal_extent_end_utc"),
            semantic_scope=data.get("semantic_scope", ""),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            limitations=tuple(data.get("limitations", [])),
            diagnostics=tuple(data.get("diagnostics", [])),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = [
    "GroundingKind",
    "KnowledgeMemoryGrounding",
]
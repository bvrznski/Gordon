# Knowledge Persistence Candidate
# ===============================

"""
Knowledge Persistence Candidate: Package for Memory admission.

This module defines the persistence candidate model that packages a Knowledge
Artifact for retention in Memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


@dataclass(frozen=True)
class KnowledgeMemoryCandidate:
    """
    A Knowledge Artifact prepared for persistence through Memory.
    
    The candidate is not itself an admitted Memory Artifact - it's a package
    that Memory may or may not admit.
    
    Fields:
        candidate_identity:      Unique ID for this persistence candidate
        
        # Source Knowledge side
        source_knowledge_artifact_id: The original Knowledge artifact
        semantic_identity:       Semantic identity of the artifact
        semantic_revision:       Revision number
        
        # Artifact kind and serialization
        artifact_kind:           What kind of artifact? (concept, belief, etc.)
        serialized_semantic_content: Serialized representation
        
        # Grounding and justification references
        grounding_references:    References to grounding records
        justification_references: References to justifications
        
        # Evidence references
        source_evidence_references: Evidence used in construction
        
        # Quality metrics
        confidence:              Confidence in this candidate (0.0-1.0)
        uncertainty:             Uncertainty about correctness
        
        # Conflicts and limitations
        conflicts:               Known conflicts with existing Knowledge
        limitations:             Known limitations of this candidate
        
        # Persistence parameters
        desired_memory_form:     Preferred Memory representation form
        retention_hint:          How long should this be retained?
        retrieval_hint:          How might this be retrieved later?
        
        # Supersession context
        supersession_context:    Context for superseding older revisions
        
        # Provenance
        provenance:              How was this candidate prepared?
    """
    
    # Identity (required)
    candidate_identity: str                   # Unique ID
    
    # Source Knowledge side
    source_knowledge_artifact_id: str         # Original artifact
    semantic_identity: str                    # Semantic identity
    semantic_revision: int = 1                # Revision number
    
    # Artifact kind and serialization
    artifact_kind: str = "unknown"            # concept, proposition, belief, etc.
    serialized_semantic_content: Dict[str, Any] = field(default_factory=dict)
    
    # References
    grounding_references: Tuple[str, ...] = field(default_factory=tuple)
    justification_references: Tuple[str, ...] = field(default_factory=tuple)
    source_evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    
    # Quality metrics (required)
    confidence: float = 0.5                   # Confidence in candidate
    uncertainty: float = 0.5                  # Uncertainty about correctness
    
    # Conflicts and limitations
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Persistence parameters
    desired_memory_form: str = "standard"     # preferred form for Memory
    retention_hint: str = "cross_session"     # retention duration hint
    retrieval_hint: str = "semantic_search"   # retrieval method hint
    
    # Supersession context
    supersession_context: Optional[Dict[str, Any]] = None
    
    # Provenance (required)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate candidate."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
    
    @property
    def is_complete_candidate(self) -> bool:
        """Check if this candidate has minimal required data."""
        return (
            len(self.candidate_identity) > 0 and
            len(self.semantic_identity) > 0 and
            len(self.artifact_kind) > 0 and
            len(self.serialized_semantic_content) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary for serialization."""
        return {
            "candidate_identity": self.candidate_identity,
            "source_knowledge_artifact_id": self.source_knowledge_artifact_id,
            "semantic_identity": self.semantic_identity,
            "semantic_revision": self.semantic_revision,
            "artifact_kind": self.artifact_kind,
            "serialized_semantic_content": dict(self.serialized_semantic_content),
            "grounding_references": list(self.grounding_references),
            "justification_references": list(self.justification_references),
            "source_evidence_references": list(self.source_evidence_references),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "conflicts": [c if isinstance(c, dict) else c.to_dict() if hasattr(c, 'to_dict') else {} for c in self.conflicts],
            "limitations": list(self.limitations),
            "desired_memory_form": self.desired_memory_form,
            "retention_hint": self.retention_hint,
            "retrieval_hint": self.retrieval_hint,
            "supersession_context": dict(self.supersession_context) if self.supersession_context else None,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeMemoryCandidate":
        """Create candidate from dictionary."""
        return cls(
            candidate_identity=data.get("candidate_identity", str(uuid.uuid4())),
            source_knowledge_artifact_id=data.get("source_knowledge_artifact_id", ""),
            semantic_identity=data.get("semantic_identity", ""),
            semantic_revision=int(data.get("semantic_revision", 1)),
            artifact_kind=data.get("artifact_kind", "unknown"),
            serialized_semantic_content=dict(data.get("serialized_semantic_content", {})),
            grounding_references=tuple(data.get("grounding_references", [])),
            justification_references=tuple(data.get("justification_references", [])),
            source_evidence_references=tuple(data.get("source_evidence_references", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            conflicts=tuple(data.get("conflicts", [])),
            limitations=tuple(data.get("limitations", [])),
            desired_memory_form=data.get("desired_memory_form", "standard"),
            retention_hint=data.get("retention_hint", "cross_session"),
            retrieval_hint=data.get("retrieval_hint", "semantic_search"),
            supersession_context=data.get("supersession_context"),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = ["KnowledgeMemoryCandidate"]